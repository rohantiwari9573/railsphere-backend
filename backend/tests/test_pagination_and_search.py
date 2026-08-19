from datetime import time

from app.models.schedule import Schedule


async def test_stations_list_is_paginated(client):
    for i in range(5):
        await client.post(
            "/stations",
            json={"code": f"PG{i}", "name": f"Pagination Station {i}"},
        )

    response = await client.get("/stations?limit=2&skip=0")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 5
    assert len(body["items"]) == 2
    assert body["skip"] == 0
    assert body["limit"] == 2


async def test_stations_search_filters_by_name_or_code(client):
    await client.post(
        "/stations", json={"code": "SRCH", "name": "Search Target"}
    )
    await client.post(
        "/stations", json={"code": "OTHR", "name": "Unrelated"}
    )

    response = await client.get("/stations?search=Search Target")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["code"] == "SRCH"


async def test_journey_search_between_stations(client, db_session):
    route = await client.post(
        "/routes",
        json={"route_code": "JSR-RTE", "route_name": "Journey Search Route"},
    )
    route_id = route.json()["id"]

    station_a = await client.post(
        "/stations", json={"code": "JSA", "name": "Journey Station A"}
    )
    station_b = await client.post(
        "/stations", json={"code": "JSB", "name": "Journey Station B"}
    )
    a_id = station_a.json()["id"]
    b_id = station_b.json()["id"]

    await client.post(
        "/route-stations",
        json={
            "route_id": route_id,
            "station_id": a_id,
            "sequence_number": 1,
            "departure_time": "08:00:00",
        },
    )
    await client.post(
        "/route-stations",
        json={
            "route_id": route_id,
            "station_id": b_id,
            "sequence_number": 2,
            "arrival_time": "10:00:00",
        },
    )

    train = await client.post(
        "/trains",
        json={
            "train_number": "JSTR1",
            "train_name": "Journey Search Train",
            "train_type": "Express",
        },
    )
    train_id = train.json()["id"]

    # No POST /schedules endpoint exists (schedules only come from the
    # importer) -- insert one directly for this test.
    db_session.add(
        Schedule(
            train_id=train_id,
            route_id=route_id,
            start_time=time(8, 0),
            end_time=time(10, 0),
        )
    )
    await db_session.commit()

    response = await client.get(
        f"/journeys/search?from_station_id={a_id}&to_station_id={b_id}"
    )

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["train_number"] == "JSTR1"
    assert results[0]["departure_time"] == "08:00:00"
    assert results[0]["arrival_time"] == "10:00:00"

    # Wrong direction: nothing on this route goes from B back to A.
    reverse_response = await client.get(
        f"/journeys/search?from_station_id={b_id}&to_station_id={a_id}"
    )
    assert reverse_response.json() == []


async def test_journey_search_rejects_same_station(client):
    station = await client.post(
        "/stations", json={"code": "SAME", "name": "Same Station"}
    )
    station_id = station.json()["id"]

    response = await client.get(
        f"/journeys/search?from_station_id={station_id}&to_station_id={station_id}"
    )

    assert response.status_code == 400
