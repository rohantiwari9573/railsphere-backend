from datetime import date, timedelta

import pytest

from app.core.rail_classes import compute_seat_allocation
from app.models.booking import Booking, Passenger

FUTURE_DATE = (date.today() + timedelta(days=10)).isoformat()


@pytest.fixture
async def booking_fixture(client):
    register = await client.post(
        "/auth/register",
        json={
            "full_name": "Booking Tester",
            "email": "booker@example.com",
            "password": "TestPass123!",
        },
    )
    user_id = register.json()["id"]

    login = await client.post(
        "/auth/login",
        data={"username": "booker@example.com", "password": "TestPass123!"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    train = await client.post(
        "/trains",
        json={
            "train_number": "50001",
            "train_name": "Test Express",
            "train_type": "Exp",
            "distance_km": 500,
        },
    )
    train_id = train.json()["id"]

    route = await client.post(
        "/routes",
        json={"route_code": "BK-RTE", "route_name": "Booking Test Route"},
    )
    route_id = route.json()["id"]

    source = await client.post(
        "/stations", json={"code": "BKSRC", "name": "Source Station"}
    )
    destination = await client.post(
        "/stations", json={"code": "BKDST", "name": "Destination Station"}
    )
    source_id = source.json()["id"]
    destination_id = destination.json()["id"]

    await client.post(
        "/route-stations",
        json={
            "route_id": route_id,
            "station_id": source_id,
            "sequence_number": 1,
            "distance_from_source": "0.00",
        },
    )
    await client.post(
        "/route-stations",
        json={
            "route_id": route_id,
            "station_id": destination_id,
            "sequence_number": 2,
            "distance_from_source": "500.00",
        },
    )

    return {
        "user_id": user_id,
        "headers": headers,
        "train_id": train_id,
        "route_id": route_id,
        "source_id": source_id,
        "destination_id": destination_id,
    }


def _booking_payload(fx, travel_class="SL", passengers=None):
    return {
        "train_id": fx["train_id"],
        "route_id": fx["route_id"],
        "source_station_id": fx["source_id"],
        "destination_station_id": fx["destination_id"],
        "journey_date": FUTURE_DATE,
        "travel_class": travel_class,
        "passengers": passengers
        or [{"name": "Passenger One", "age": 30, "gender": "M"}],
    }


async def test_availability_lists_allowed_classes(client, booking_fixture):
    response = await client.get(
        f"/trains/{booking_fixture['train_id']}/availability",
        params={"journey_date": FUTURE_DATE},
    )

    assert response.status_code == 200
    codes = {c["class_code"] for c in response.json()}
    assert codes == {"SL", "3A", "2A"}


async def test_create_booking_confirms_seats(client, booking_fixture):
    response = await client.post(
        "/bookings",
        json=_booking_payload(
            booking_fixture,
            passengers=[
                {"name": "Passenger One", "age": 30, "gender": "M"},
                {"name": "Passenger Two", "age": 28, "gender": "F"},
            ],
        ),
        headers=booking_fixture["headers"],
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "CONFIRMED"
    assert len(body["pnr"]) == 10
    assert body["is_paid"] is False
    assert [p["seat_number"] for p in body["passengers"]] == [1, 2]
    assert body["passengers"][0]["coach"] == "S1"
    # 500km * 0.45/km + reservation(20) = 245
    assert float(body["total_fare"]) == 490.0


async def test_create_booking_rejects_unavailable_class(client, booking_fixture):
    response = await client.post(
        "/bookings",
        json=_booking_payload(booking_fixture, travel_class="1A"),
        headers=booking_fixture["headers"],
    )

    assert response.status_code == 400
    assert "not offered" in response.json()["detail"]


async def test_create_booking_requires_auth(client, booking_fixture):
    response = await client.post(
        "/bookings", json=_booking_payload(booking_fixture)
    )

    assert response.status_code == 401


async def test_pnr_status_lookup_is_public(client, booking_fixture):
    create = await client.post(
        "/bookings",
        json=_booking_payload(booking_fixture),
        headers=booking_fixture["headers"],
    )
    pnr = create.json()["pnr"]

    response = await client.get(f"/bookings/pnr/{pnr}")

    assert response.status_code == 200
    assert response.json()["pnr"] == pnr


async def test_pnr_status_unknown_returns_404(client):
    response = await client.get("/bookings/pnr/0000000000")
    assert response.status_code == 404


async def test_pay_success(client, booking_fixture, monkeypatch):
    monkeypatch.setattr(
        "app.services.booking_service.random.random", lambda: 0.9
    )

    create = await client.post(
        "/bookings",
        json=_booking_payload(booking_fixture),
        headers=booking_fixture["headers"],
    )
    booking_id = create.json()["id"]

    response = await client.post(
        f"/bookings/{booking_id}/pay",
        json={"method": "upi"},
        headers=booking_fixture["headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["booking"]["is_paid"] is True


async def test_pay_failure_leaves_booking_unpaid(client, booking_fixture, monkeypatch):
    monkeypatch.setattr(
        "app.services.booking_service.random.random", lambda: 0.01
    )

    create = await client.post(
        "/bookings",
        json=_booking_payload(booking_fixture),
        headers=booking_fixture["headers"],
    )
    booking_id = create.json()["id"]

    response = await client.post(
        f"/bookings/{booking_id}/pay",
        json={"method": "upi"},
        headers=booking_fixture["headers"],
    )

    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"


async def test_list_my_bookings(client, booking_fixture):
    await client.post(
        "/bookings",
        json=_booking_payload(booking_fixture),
        headers=booking_fixture["headers"],
    )

    response = await client.get("/bookings/mine", headers=booking_fixture["headers"])

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_cancel_promotes_waitlisted_passenger(
    client, db_session, booking_fixture
):
    """
    Fills 1A (capacity 24 on a Rajdhani-type train) to capacity via
    direct ORM inserts, books one more passenger through the API (who
    should land on the waitlist), then cancels one of the filler
    confirmed bookings and confirms the waitlisted passenger is
    promoted into the freed seat.
    """
    raj_train = await client.post(
        "/trains",
        json={
            "train_number": "50002",
            "train_name": "Test Rajdhani",
            "train_type": "Raj",
            "distance_km": 500,
        },
    )
    train_id = raj_train.json()["id"]

    filler_booking = Booking(
        pnr="9999999999",
        user_id=booking_fixture["user_id"],
        train_id=train_id,
        route_id=booking_fixture["route_id"],
        source_station_id=booking_fixture["source_id"],
        destination_station_id=booking_fixture["destination_id"],
        journey_date=date.fromisoformat(FUTURE_DATE),
        travel_class="1A",
        status="CONFIRMED",
        total_fare="0",
    )
    for seat_number in range(1, 25):
        coach, berth = compute_seat_allocation("1A", seat_number)
        filler_booking.passengers.append(
            Passenger(
                name=f"Filler {seat_number}",
                age=30,
                gender="M",
                status="CONFIRMED",
                seat_number=seat_number,
                coach=coach,
                berth_type=berth,
            )
        )
    db_session.add(filler_booking)
    await db_session.commit()
    await db_session.refresh(filler_booking)

    waitlisted = await client.post(
        "/bookings",
        json=_booking_payload(
            {**booking_fixture, "train_id": train_id}, travel_class="1A"
        ),
        headers=booking_fixture["headers"],
    )
    assert waitlisted.status_code == 201
    assert waitlisted.json()["status"] == "WAITLISTED"
    assert waitlisted.json()["passengers"][0]["seat_number"] is None
    pnr = waitlisted.json()["pnr"]

    cancel = await client.post(
        f"/bookings/{filler_booking.id}/cancel",
        headers=booking_fixture["headers"],
    )
    assert cancel.status_code == 200

    lookup = await client.get(f"/bookings/pnr/{pnr}")
    body = lookup.json()
    assert body["status"] == "CONFIRMED"
    assert body["passengers"][0]["status"] == "CONFIRMED"
    assert body["passengers"][0]["seat_number"] == 1
