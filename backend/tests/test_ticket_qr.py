from datetime import date
from urllib.parse import parse_qs, urlparse

import pytest

from app.core.config import settings
from app.core.ticket_signing import parse_ticket, sign_ticket
from tests.test_booking import FUTURE_DATE, _booking_payload, booking_fixture  # noqa: F401


def test_ticket_token_round_trips():
    assert parse_ticket(sign_ticket("5371241850")) == "5371241850"


def test_ticket_token_rejects_tampered_pnr():
    token = sign_ticket("5371241850")
    _, _, signature = token.split(".")
    assert parse_ticket(f"RSV1.1111111111.{signature}") is None


def test_ticket_token_rejects_bad_signature_and_garbage():
    assert parse_ticket("RSV1.5371241850.deadbeef") is None
    assert parse_ticket("RS PNR 5371241850 | 12138 | 2026-09-25") is None
    assert parse_ticket("") is None


async def _create_booking(client, fx, journey_date=FUTURE_DATE):
    payload = {**_booking_payload(fx), "journey_date": journey_date}
    response = await client.post(
        "/bookings", json=payload, headers=fx["headers"]
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _pay(client, fx, booking_id, monkeypatch, succeed=True):
    monkeypatch.setattr(
        "app.services.booking_service.random.random",
        lambda: 0.9 if succeed else 0.01,
    )
    response = await client.post(
        f"/bookings/{booking_id}/pay",
        json={"method": "UPI"},
        headers=fx["headers"],
    )
    return response.json()


async def test_booking_response_carries_verifiable_qr_payload(
    client, booking_fixture
):
    booking = await _create_booking(client, booking_fixture)
    assert parse_ticket(booking["qr_payload"]) == booking["pnr"]
    assert booking["checked_in_at"] is None


async def test_upi_intent_disabled_without_payee_configured(
    client, booking_fixture, monkeypatch
):
    monkeypatch.setattr(settings, "UPI_PAYEE_VPA", "")
    booking = await _create_booking(client, booking_fixture)
    response = await client.post(
        f"/bookings/{booking['id']}/upi-intent",
        headers=booking_fixture["headers"],
    )
    assert response.status_code == 400
    assert "not configured" in response.json()["detail"]


async def test_upi_intent_is_bound_to_booking_amount_and_fresh_each_time(
    client, booking_fixture, monkeypatch
):
    monkeypatch.setattr(settings, "UPI_PAYEE_VPA", "railsphere@testbank")
    booking = await _create_booking(client, booking_fixture)

    first = await client.post(
        f"/bookings/{booking['id']}/upi-intent",
        headers=booking_fixture["headers"],
    )
    second = await client.post(
        f"/bookings/{booking['id']}/upi-intent",
        headers=booking_fixture["headers"],
    )
    assert first.status_code == second.status_code == 200

    first_body, second_body = first.json(), second.json()
    assert first_body["transaction_reference"] != second_body["transaction_reference"]
    assert first_body["transaction_reference"].startswith(f"RS{booking['pnr']}")

    query = parse_qs(urlparse(first_body["upi_uri"]).query)
    assert urlparse(first_body["upi_uri"]).scheme == "upi"
    assert query["pa"] == ["railsphere@testbank"]
    assert query["am"] == [f"{float(booking['total_fare']):.2f}"]
    assert query["cu"] == ["INR"]


async def test_upi_intent_refused_once_paid(
    client, booking_fixture, monkeypatch
):
    monkeypatch.setattr(settings, "UPI_PAYEE_VPA", "railsphere@testbank")
    booking = await _create_booking(client, booking_fixture)
    await _pay(client, booking_fixture, booking["id"], monkeypatch)

    response = await client.post(
        f"/bookings/{booking['id']}/upi-intent",
        headers=booking_fixture["headers"],
    )
    assert response.status_code == 400
    assert "already been paid" in response.json()["detail"]


async def test_verify_checks_in_a_paid_ticket_exactly_once(
    client, booking_fixture, admin_headers, monkeypatch
):
    today = date.today().isoformat()
    booking = await _create_booking(client, booking_fixture, journey_date=today)
    await _pay(client, booking_fixture, booking["id"], monkeypatch)
    token = (
        await client.get(
            f"/bookings/{booking['id']}", headers=booking_fixture["headers"]
        )
    ).json()["qr_payload"]

    first = await client.post(
        "/tickets/verify", json={"token": token}, headers=admin_headers
    )
    assert first.json()["valid"] is True
    assert first.json()["booking"]["checked_in_at"] is not None

    second = await client.post(
        "/tickets/verify", json={"token": token}, headers=admin_headers
    )
    assert second.json()["valid"] is False
    assert "already checked in" in second.json()["reason"]


async def test_verify_rejects_unpaid_ticket(
    client, booking_fixture, admin_headers
):
    today = date.today().isoformat()
    booking = await _create_booking(client, booking_fixture, journey_date=today)
    response = await client.post(
        "/tickets/verify",
        json={"token": sign_ticket(booking["pnr"])},
        headers=admin_headers,
    )
    assert response.json()["valid"] is False
    assert "not been paid" in response.json()["reason"]


async def test_verify_rejects_ticket_for_another_day(
    client, booking_fixture, admin_headers, monkeypatch
):
    booking = await _create_booking(client, booking_fixture)
    await _pay(client, booking_fixture, booking["id"], monkeypatch)
    response = await client.post(
        "/tickets/verify",
        json={"token": booking["qr_payload"]},
        headers=admin_headers,
    )
    assert response.json()["valid"] is False
    assert "not today" in response.json()["reason"]


async def test_verify_rejects_forged_token(client, admin_headers):
    response = await client.post(
        "/tickets/verify",
        json={"token": "RSV1.5371241850.0123456789abcdef01234567"},
        headers=admin_headers,
    )
    assert response.json()["valid"] is False
    assert response.json()["booking"] is None


async def test_verify_is_staff_only(client, booking_fixture):
    response = await client.post(
        "/tickets/verify",
        json={"token": "RSV1.x.y"},
        headers=booking_fixture["headers"],
    )
    assert response.status_code == 403
