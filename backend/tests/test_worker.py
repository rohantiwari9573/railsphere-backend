from sqlalchemy import text

from app.db.database import AsyncSessionLocal
from app.models.route import Route
from app.models.route_station import RouteStation
from app.models.station import Station
from app.worker import refresh_analytics_views


async def test_refresh_analytics_views_job_runs_and_updates_the_views():
    """
    The arq job opens its own session (AsyncSessionLocal), a separate
    connection from the one the `db_session`/`client` fixtures use --
    so it can't see the other tests' uncommitted savepoint data, and
    other tests can't see what this one commits either. This test
    therefore commits its own fixture data for real and cleans it up
    itself, rather than relying on the usual rollback-based isolation.
    """
    async with AsyncSessionLocal() as db:
        station = Station(code="WKRTST", name="Worker Job Station")
        route = Route(route_code="WKRTST-RTE", route_name="Worker Job Route")
        db.add_all([station, route])
        await db.commit()
        await db.refresh(station)
        await db.refresh(route)

        db.add(
            RouteStation(
                route_id=route.id,
                station_id=station.id,
                sequence_number=1,
            )
        )
        await db.commit()

        station_id = station.id

    try:
        async with AsyncSessionLocal() as db:
            before = await db.execute(
                text(
                    "SELECT count(*) FROM mv_top_stations "
                    "WHERE station_id = :id"
                ),
                {"id": station_id},
            )
            assert before.scalar_one() == 0

        await refresh_analytics_views(ctx={})

        async with AsyncSessionLocal() as db:
            after = await db.execute(
                text(
                    "SELECT count(*) FROM mv_top_stations "
                    "WHERE station_id = :id"
                ),
                {"id": station_id},
            )
            assert after.scalar_one() == 1
    finally:
        async with AsyncSessionLocal() as db:
            await db.execute(
                text(
                    "DELETE FROM route_stations WHERE station_id = :id"
                ),
                {"id": station_id},
            )
            await db.execute(
                text("DELETE FROM stations WHERE id = :id"),
                {"id": station_id},
            )
            await db.execute(
                text("DELETE FROM routes WHERE route_code = :code"),
                {"code": "WKRTST-RTE"},
            )
            await db.commit()

        await refresh_analytics_views(ctx={})
