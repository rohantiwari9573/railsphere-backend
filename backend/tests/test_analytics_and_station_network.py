from datetime import time

from app.models.schedule import Schedule


async def test_analytics_overview_reflects_real_counts(client):
    await client.post("/stations", json={"code": "AN1", "name": "Analytics One"})
    await client.post("/stations", json={"code": "AN2", "name": "Analytics Two"})
    route = await client.post(
        "/routes", json={"route_code": "AN-RTE", "route_name": "Analytics Route"}
    )
    route_id = route.json()["id"]

    response = await client.get("/analytics/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["total_stations"] >= 2
    assert body["total_routes"] >= 1
    assert isinstance(body["avg_stations_per_route"], float)


async def test_top_stations_ranks_by_route_count(client):
    route_a = await client.post(
        "/routes", json={"route_code": "TSA", "route_name": "Route A"}
    )
    route_b = await client.post(
        "/routes", json={"route_code": "TSB", "route_name": "Route B"}
    )
    station = await client.post(
        "/stations", json={"code": "POP", "name": "Popular Station"}
    )
    station_id = station.json()["id"]

    await client.post(
        "/route-stations",
        json={
            "route_id": route_a.json()["id"],
            "station_id": station_id,
            "sequence_number": 1,
        },
    )
    await client.post(
        "/route-stations",
        json={
            "route_id": route_b.json()["id"],
            "station_id": station_id,
            "sequence_number": 1,
        },
    )

    response = await client.get("/analytics/top-stations?limit=50")

    assert response.status_code == 200
    matching = [
        row for row in response.json() if row["station_id"] == station_id
    ]
    assert len(matching) == 1
    assert matching[0]["route_count"] == 2


async def test_station_routes_and_trains(client, db_session):
    route = await client.post(
        "/routes", json={"route_code": "SRT-RTE", "route_name": "Station Route"}
    )
    route_id = route.json()["id"]

    station = await client.post(
        "/stations", json={"code": "SRT", "name": "Station Route Target"}
    )
    station_id = station.json()["id"]

    await client.post(
        "/route-stations",
        json={
            "route_id": route_id,
            "station_id": station_id,
            "sequence_number": 1,
            "departure_time": "09:00:00",
        },
    )

    routes_response = await client.get(f"/stations/{station_id}/routes")
    assert routes_response.status_code == 200
    assert len(routes_response.json()) == 1
    assert routes_response.json()[0]["route_id"] == route_id

    train = await client.post(
        "/trains",
        json={
            "train_number": "SRTTR",
            "train_name": "Station Route Train",
            "train_type": "Express",
        },
    )
    train_id = train.json()["id"]

    db_session.add(
        Schedule(
            train_id=train_id,
            route_id=route_id,
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
    )
    await db_session.commit()

    trains_response = await client.get(f"/stations/{station_id}/trains")
    assert trains_response.status_code == 200
    assert len(trains_response.json()) == 1
    assert trains_response.json()[0]["train_number"] == "SRTTR"


async def test_station_routes_404_for_missing_station(client):
    response = await client.get("/stations/999999/routes")
    assert response.status_code == 404
