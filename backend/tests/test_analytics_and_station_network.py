from datetime import time

from app.models.schedule import Schedule
from app.repositories.analytics_repository import AnalyticsRepository


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


async def test_top_stations_ranks_by_route_count(client, db_session):
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

    # top-stations is served from a materialized view (see
    # AnalyticsRepository.refresh_views) which only picks up new rows
    # once refreshed -- it doesn't update live on every insert.
    await AnalyticsRepository(db_session).refresh_views()

    response = await client.get("/analytics/top-stations?limit=50")

    assert response.status_code == 200
    matching = [
        row for row in response.json() if row["station_id"] == station_id
    ]
    assert len(matching) == 1
    assert matching[0]["route_count"] == 2


async def test_top_stations_is_stale_until_refreshed(client, db_session):
    route = await client.post(
        "/routes", json={"route_code": "STL-RTE", "route_name": "Stale Route"}
    )
    station = await client.post(
        "/stations", json={"code": "STL", "name": "Stale Station"}
    )
    station_id = station.json()["id"]

    await client.post(
        "/route-stations",
        json={
            "route_id": route.json()["id"],
            "station_id": station_id,
            "sequence_number": 1,
        },
    )

    before = await client.get("/analytics/top-stations?limit=50")
    assert all(
        row["station_id"] != station_id for row in before.json()
    )

    await AnalyticsRepository(db_session).refresh_views()

    after = await client.get("/analytics/top-stations?limit=50")
    assert any(row["station_id"] == station_id for row in after.json())


async def test_top_routes_ranks_by_stop_count(client, db_session):
    route = await client.post(
        "/routes", json={"route_code": "TRR", "route_name": "Top Route"}
    )
    route_id = route.json()["id"]

    for i in range(3):
        station = await client.post(
            "/stations", json={"code": f"TRR{i}", "name": f"Top Route Stop {i}"}
        )
        await client.post(
            "/route-stations",
            json={
                "route_id": route_id,
                "station_id": station.json()["id"],
                "sequence_number": i + 1,
            },
        )

    await AnalyticsRepository(db_session).refresh_views()

    response = await client.get("/analytics/top-routes?limit=50")

    assert response.status_code == 200
    matching = [row for row in response.json() if row["route_id"] == route_id]
    assert len(matching) == 1
    assert matching[0]["stop_count"] == 3


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


async def test_train_routes(client, db_session):
    route = await client.post(
        "/routes", json={"route_code": "TRT-RTE", "route_name": "Train Route"}
    )
    route_id = route.json()["id"]

    train = await client.post(
        "/trains",
        json={
            "train_number": "TRTTR",
            "train_name": "Train Route Train",
            "train_type": "Express",
        },
    )
    train_id = train.json()["id"]

    db_session.add(
        Schedule(
            train_id=train_id,
            route_id=route_id,
            start_time=time(6, 0),
            end_time=time(14, 0),
        )
    )
    await db_session.commit()

    response = await client.get(f"/trains/{train_id}/routes")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["route_id"] == route_id
    assert body[0]["start_time"] == "06:00:00"
    assert body[0]["end_time"] == "14:00:00"


async def test_train_routes_404_for_missing_train(client):
    response = await client.get("/trains/999999/routes")
    assert response.status_code == 404
