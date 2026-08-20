from app.models.station import Station
from app.models.train import Train


async def test_station_get_is_cached_until_update_invalidates(
    cached_client, db_session
):
    created = await cached_client.post(
        "/stations", json={"code": "CACH", "name": "Cache Original"}
    )
    station_id = created.json()["id"]

    first = await cached_client.get(f"/stations/{station_id}")
    assert first.json()["name"] == "Cache Original"

    # Mutate directly in the DB, bypassing the service layer (and its
    # cache invalidation), to prove the next read comes from cache
    # rather than re-querying the database.
    db_obj = await db_session.get(Station, station_id)
    db_obj.name = "Mutated Behind Cache's Back"
    await db_session.commit()

    second = await cached_client.get(f"/stations/{station_id}")
    assert second.json()["name"] == "Cache Original"

    # A real update goes through the service, which invalidates.
    await cached_client.put(
        f"/stations/{station_id}", json={"name": "Cache Updated"}
    )

    third = await cached_client.get(f"/stations/{station_id}")
    assert third.json()["name"] == "Cache Updated"


async def test_station_get_cache_is_invalidated_on_delete(
    cached_client, fake_redis
):
    created = await cached_client.post(
        "/stations", json={"code": "CACHD", "name": "To Delete"}
    )
    station_id = created.json()["id"]

    await cached_client.get(f"/stations/{station_id}")
    assert await fake_redis.get(f"station:{station_id}") is not None

    await cached_client.delete(f"/stations/{station_id}")
    assert await fake_redis.get(f"station:{station_id}") is None


async def test_train_get_is_cached_until_update_invalidates(
    cached_client, db_session
):
    created = await cached_client.post(
        "/trains",
        json={
            "train_number": "CACH01",
            "train_name": "Cache Train",
            "train_type": "Express",
        },
    )
    train_id = created.json()["id"]

    first = await cached_client.get(f"/trains/{train_id}")
    assert first.json()["train_name"] == "Cache Train"

    db_obj = await db_session.get(Train, train_id)
    db_obj.train_name = "Mutated Behind Cache's Back"
    await db_session.commit()

    second = await cached_client.get(f"/trains/{train_id}")
    assert second.json()["train_name"] == "Cache Train"

    await cached_client.put(
        f"/trains/{train_id}", json={"train_name": "Cache Train Updated"}
    )

    third = await cached_client.get(f"/trains/{train_id}")
    assert third.json()["train_name"] == "Cache Train Updated"


async def test_analytics_overview_is_cached(cached_client, fake_redis):
    response = await cached_client.get("/analytics/overview")
    assert response.status_code == 200

    cached = await fake_redis.get("analytics:overview")
    assert cached is not None

    ttl = await fake_redis.ttl("analytics:overview")
    assert ttl > 0


async def test_analytics_train_types_is_cached(cached_client, fake_redis):
    response = await cached_client.get("/analytics/train-types")
    assert response.status_code == 200

    cached = await fake_redis.get("analytics:train-types")
    assert cached is not None
