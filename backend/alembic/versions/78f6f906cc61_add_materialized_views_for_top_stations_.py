"""add materialized views for top stations and top routes

Revision ID: 78f6f906cc61
Revises: 3a62537e18a0
Create Date: 2026-08-20 22:07:20.732651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78f6f906cc61'
down_revision: Union[str, Sequence[str], None] = '3a62537e18a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Precomputes the two analytics rankings that previously required a
    # live JOIN + GROUP BY + ORDER BY over route_stations (415k+ rows)
    # on every request. Populated immediately on creation; refreshed
    # afterwards via REFRESH MATERIALIZED VIEW CONCURRENTLY, which
    # needs the unique indexes below.
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
