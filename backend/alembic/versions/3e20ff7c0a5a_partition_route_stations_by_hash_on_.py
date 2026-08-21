"""partition route_stations by hash on route_id

Revision ID: 3e20ff7c0a5a
Revises: 262fb9ec2558
Create Date: 2026-08-21 14:03:03.641635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e20ff7c0a5a'
down_revision: Union[str, Sequence[str], None] = '262fb9ec2558'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_PARTITION_COUNT = 8


def upgrade() -> None:
    """
    Converts route_stations (415k+ rows) into a hash-partitioned table
    on route_id, split across 8 partitions. Almost every query against
    this table filters by route_id (get all stops for a route), so the
    planner can prune straight to one partition instead of scanning
    the whole table.

    Postgres requires any unique/primary key on a partitioned table to
    include the partition key column. uq_route_sequence and
    uq_route_station already do (both include route_id), but the bare
    `id` primary key doesn't, so it becomes a composite (id, route_id)
    key here -- id values still come from one shared sequence and stay
    globally unique in practice, just not DB-enforced as such anymore.
    Nothing in the app does session.get(RouteStation, id)-style single-
    column PK lookups, so this doesn't require any repository/service
    changes.

    mv_top_stations/mv_top_routes (78f6f906cc61) select from
    route_stations, and a materialized view depends on the underlying
    table by OID -- renaming route_stations doesn't move that
    dependency, so both views have to be dropped and recreated against
    the new table rather than just left alone.
    """
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_top_routes")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_top_stations")

    op.execute("ALTER TABLE route_stations RENAME TO route_stations_legacy")
    op.execute(
        "ALTER TABLE route_stations_legacy RENAME CONSTRAINT "
        "route_stations_pkey TO route_stations_legacy_pkey"
    )
    op.execute(
        "ALTER TABLE route_stations_legacy RENAME CONSTRAINT "
        "uq_route_sequence TO uq_route_sequence_legacy"
    )
    op.execute(
        "ALTER TABLE route_stations_legacy RENAME CONSTRAINT "
        "uq_route_station TO uq_route_station_legacy"
    )
    op.execute(
        "ALTER TABLE route_stations_legacy RENAME CONSTRAINT "
        "route_stations_route_id_fkey TO route_stations_legacy_route_id_fkey"
    )
    op.execute(
        "ALTER TABLE route_stations_legacy RENAME CONSTRAINT "
        "route_stations_station_id_fkey "
        "TO route_stations_legacy_station_id_fkey"
    )
    op.execute(
        "ALTER INDEX ix_route_station_route_sequence "
        "RENAME TO ix_route_station_route_sequence_legacy"
    )
    op.execute(
        "ALTER INDEX ix_route_stations_id "
        "RENAME TO ix_route_stations_id_legacy"
    )

    op.execute("""
        CREATE TABLE route_stations (
            id INTEGER NOT NULL DEFAULT nextval('route_stations_id_seq'),
            route_id INTEGER NOT NULL,
            station_id INTEGER NOT NULL,
            sequence_number INTEGER NOT NULL,
            arrival_time TIME,
            departure_time TIME,
            halt_minutes INTEGER NOT NULL DEFAULT 0,
            distance_from_source NUMERIC(8, 2) NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT route_stations_pkey PRIMARY KEY (id, route_id),
            CONSTRAINT uq_route_sequence UNIQUE (route_id, sequence_number),
            CONSTRAINT uq_route_station UNIQUE (route_id, station_id),
            CONSTRAINT route_stations_route_id_fkey
                FOREIGN KEY (route_id) REFERENCES routes(id)
                ON DELETE CASCADE,
            CONSTRAINT route_stations_station_id_fkey
                FOREIGN KEY (station_id) REFERENCES stations(id)
                ON DELETE CASCADE
        ) PARTITION BY HASH (route_id)
    """)

    for i in range(_PARTITION_COUNT):
        op.execute(f"""
            CREATE TABLE route_stations_p{i}
            PARTITION OF route_stations
            FOR VALUES WITH (MODULUS {_PARTITION_COUNT}, REMAINDER {i})
        """)

    op.execute(
        "CREATE INDEX ix_route_station_route_sequence "
        "ON route_stations (route_id, sequence_number)"
    )
    op.execute(
        "CREATE INDEX ix_route_stations_id ON route_stations (id)"
    )

    op.execute("""
        INSERT INTO route_stations (
            id, route_id, station_id, sequence_number, arrival_time,
            departure_time, halt_minutes, distance_from_source,
            created_at, updated_at
        )
        SELECT
            id, route_id, station_id, sequence_number, arrival_time,
            departure_time, halt_minutes, distance_from_source,
            created_at, updated_at
        FROM route_stations_legacy
    """)

    # Must happen before the DROP TABLE below: route_stations_legacy.id
    # still owns this sequence (an internal, not a regular, dependency),
    # so dropping the table first would cascade-drop the sequence out
    # from under the new table's and partitions' id defaults.
    op.execute(
        "ALTER SEQUENCE route_stations_id_seq OWNED BY route_stations.id"
    )
    op.execute("DROP TABLE route_stations_legacy")

    op.execute("""
        CREATE MATERIALIZED VIEW mv_top_stations AS
        SELECT
            s.id AS station_id,
            s.name AS name,
            s.code AS code,
            COUNT(rs.id) AS route_count
        FROM stations s
        JOIN route_stations rs ON rs.station_id = s.id
        GROUP BY s.id
        ORDER BY route_count DESC
    """)
    op.execute(
        "CREATE UNIQUE INDEX ix_mv_top_stations_station_id "
        "ON mv_top_stations (station_id)"
    )
    op.execute(
        "CREATE INDEX ix_mv_top_stations_route_count "
        "ON mv_top_stations (route_count DESC)"
    )

    op.execute("""
        CREATE MATERIALIZED VIEW mv_top_routes AS
        SELECT
            r.id AS route_id,
            r.route_code AS route_code,
            r.route_name AS route_name,
            COUNT(rs.id) AS stop_count
        FROM routes r
        JOIN route_stations rs ON rs.route_id = r.id
        GROUP BY r.id
        ORDER BY stop_count DESC
    """)
    op.execute(
        "CREATE UNIQUE INDEX ix_mv_top_routes_route_id "
        "ON mv_top_routes (route_id)"
    )
    op.execute(
        "CREATE INDEX ix_mv_top_routes_stop_count "
        "ON mv_top_routes (stop_count DESC)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_top_routes")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_top_stations")

    op.execute("ALTER TABLE route_stations RENAME TO route_stations_partitioned")
    op.execute(
        "ALTER TABLE route_stations_partitioned RENAME CONSTRAINT "
        "route_stations_pkey TO route_stations_partitioned_pkey"
    )
    op.execute(
        "ALTER TABLE route_stations_partitioned RENAME CONSTRAINT "
        "uq_route_sequence TO uq_route_sequence_partitioned"
    )
    op.execute(
        "ALTER TABLE route_stations_partitioned RENAME CONSTRAINT "
        "uq_route_station TO uq_route_station_partitioned"
    )
    op.execute(
        "ALTER TABLE route_stations_partitioned RENAME CONSTRAINT "
        "route_stations_route_id_fkey "
        "TO route_stations_partitioned_route_id_fkey"
    )
    op.execute(
        "ALTER TABLE route_stations_partitioned RENAME CONSTRAINT "
        "route_stations_station_id_fkey "
        "TO route_stations_partitioned_station_id_fkey"
    )
    op.execute(
        "ALTER INDEX ix_route_station_route_sequence "
        "RENAME TO ix_route_station_route_sequence_partitioned"
    )
    op.execute(
        "ALTER INDEX ix_route_stations_id "
        "RENAME TO ix_route_stations_id_partitioned"
    )

    op.execute("""
        CREATE TABLE route_stations (
            id INTEGER NOT NULL DEFAULT nextval('route_stations_id_seq'),
            route_id INTEGER NOT NULL,
            station_id INTEGER NOT NULL,
            sequence_number INTEGER NOT NULL,
            arrival_time TIME,
            departure_time TIME,
            halt_minutes INTEGER NOT NULL DEFAULT 0,
            distance_from_source NUMERIC(8, 2) NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT route_stations_pkey PRIMARY KEY (id),
            CONSTRAINT uq_route_sequence UNIQUE (route_id, sequence_number),
            CONSTRAINT uq_route_station UNIQUE (route_id, station_id),
            CONSTRAINT route_stations_route_id_fkey
                FOREIGN KEY (route_id) REFERENCES routes(id)
                ON DELETE CASCADE,
            CONSTRAINT route_stations_station_id_fkey
                FOREIGN KEY (station_id) REFERENCES stations(id)
                ON DELETE CASCADE
        )
    """)
    op.execute(
        "CREATE INDEX ix_route_station_route_sequence "
        "ON route_stations (route_id, sequence_number)"
    )
    op.execute(
        "CREATE INDEX ix_route_stations_id ON route_stations (id)"
    )

    op.execute("""
        INSERT INTO route_stations (
            id, route_id, station_id, sequence_number, arrival_time,
            departure_time, halt_minutes, distance_from_source,
            created_at, updated_at
        )
        SELECT
            id, route_id, station_id, sequence_number, arrival_time,
            departure_time, halt_minutes, distance_from_source,
            created_at, updated_at
        FROM route_stations_partitioned
    """)

    op.execute(
        "ALTER SEQUENCE route_stations_id_seq OWNED BY route_stations.id"
    )
    op.execute("DROP TABLE route_stations_partitioned")

    op.execute("""
        CREATE MATERIALIZED VIEW mv_top_stations AS
        SELECT
            s.id AS station_id,
            s.name AS name,
            s.code AS code,
            COUNT(rs.id) AS route_count
        FROM stations s
        JOIN route_stations rs ON rs.station_id = s.id
        GROUP BY s.id
        ORDER BY route_count DESC
    """)
    op.execute(
        "CREATE UNIQUE INDEX ix_mv_top_stations_station_id "
        "ON mv_top_stations (station_id)"
    )
    op.execute(
        "CREATE INDEX ix_mv_top_stations_route_count "
        "ON mv_top_stations (route_count DESC)"
    )

    op.execute("""
        CREATE MATERIALIZED VIEW mv_top_routes AS
        SELECT
            r.id AS route_id,
            r.route_code AS route_code,
            r.route_name AS route_name,
            COUNT(rs.id) AS stop_count
        FROM routes r
        JOIN route_stations rs ON rs.route_id = r.id
        GROUP BY r.id
        ORDER BY stop_count DESC
    """)
    op.execute(
        "CREATE UNIQUE INDEX ix_mv_top_routes_route_id "
        "ON mv_top_routes (route_id)"
    )
    op.execute(
        "CREATE INDEX ix_mv_top_routes_stop_count "
        "ON mv_top_routes (stop_count DESC)"
    )
