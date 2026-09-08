import pytest


@pytest.fixture
async def route_and_stations(client, admin_headers):
    route_response = await client.post(
        "/routes",
        json={"route_code": "TST-RTE", "route_name": "Test Route"},
        headers=admin_headers,
    )
    route_id = route_response.json()["id"]

    station_a = await client.post(
        "/stations",
        json={"code": "STA", "name": "Station A"},
        headers=admin_headers,
    )
    station_b = await client.post(
        "/stations",
        json={"code": "STB", "name": "Station B"},
        headers=admin_headers,
    )

    return {
        "route_id": route_id,
        "station_a_id": station_a.json()["id"],
        "station_b_id": station_b.json()["id"],
    }


async def test_create_route_station(
    client, admin_headers, route_and_stations
):
    response = await client.post(
        "/route-stations",
        json={
            "route_id": route_and_stations["route_id"],
            "station_id": route_and_stations["station_a_id"],
            "sequence_number": 1,
        },
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["sequence_number"] == 1


async def test_duplicate_station_on_same_route_is_rejected(
    client, admin_headers, route_and_stations
):
    payload = {
        "route_id": route_and_stations["route_id"],
        "station_id": route_and_stations["station_a_id"],
        "sequence_number": 1,
    }

    first = await client.post(
        "/route-stations", json=payload, headers=admin_headers
    )
    assert first.status_code == 201

    second = await client.post(
        "/route-stations",
        json={
            **payload,
            "sequence_number": 2,
        },
        headers=admin_headers,
    )

    assert second.status_code == 400
    assert "already part of this route" in second.json()["detail"]


async def test_duplicate_sequence_number_on_same_route_is_rejected(
    client, admin_headers, route_and_stations
):
    await client.post(
        "/route-stations",
        json={
            "route_id": route_and_stations["route_id"],
            "station_id": route_and_stations["station_a_id"],
            "sequence_number": 1,
        },
        headers=admin_headers,
    )

    response = await client.post(
        "/route-stations",
        json={
            "route_id": route_and_stations["route_id"],
            "station_id": route_and_stations["station_b_id"],
            "sequence_number": 1,
        },
        headers=admin_headers,
    )

    assert response.status_code == 400
    assert "sequence number" in response.json()["detail"]


async def test_create_route_station_with_missing_route_is_rejected(
    client, admin_headers, route_and_stations
):
    response = await client.post(
        "/route-stations",
        json={
            "route_id": 999999,
            "station_id": route_and_stations["station_a_id"],
            "sequence_number": 1,
        },
        headers=admin_headers,
    )

    assert response.status_code == 400
