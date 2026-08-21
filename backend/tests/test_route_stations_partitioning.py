import re

from sqlalchemy import text


async def test_route_stations_is_hash_partitioned_by_route_id(db_session):
    result = await db_session.execute(
        text(
            "SELECT count(*) FROM pg_inherits "
            "WHERE inhparent = 'route_stations'::regclass"
        )
    )
    assert result.scalar() == 8


async def test_route_id_filter_prunes_to_a_single_partition(db_session):
    result = await db_session.execute(
        text("EXPLAIN SELECT * FROM route_stations WHERE route_id = 1")
    )
    plan = "\n".join(row[0] for row in result.fetchall())

    # A pruned plan touches exactly one partition -- if the planner had
    # to scan every partition, more than one distinct route_stations_pN
    # name would show up in the plan text.
    touched = set(re.findall(r"route_stations_p\d+", plan))
    assert len(touched) == 1
