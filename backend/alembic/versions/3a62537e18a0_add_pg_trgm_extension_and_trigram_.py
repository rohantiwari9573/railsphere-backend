"""add pg_trgm extension and trigram search indexes

Revision ID: 3a62537e18a0
Revises: 0bb6977d93aa
Create Date: 2026-08-20 22:04:52.365214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a62537e18a0'
down_revision: Union[str, Sequence[str], None] = '0bb6977d93aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # GIN trigram indexes speed up the existing ILIKE '%term%' search
    # filters (station/train search) and unlock similarity() ranking,
    # without changing any application-level query shape.
    op.execute(
        "CREATE INDEX ix_stations_name_trgm ON stations "
        "USING gin (name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_stations_code_trgm ON stations "
        "USING gin (code gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_stations_city_trgm ON stations "
        "USING gin (city gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_trains_train_name_trgm ON trains "
        "USING gin (train_name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_trains_train_number_trgm ON trains "
        "USING gin (train_number gin_trgm_ops)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_trains_train_number_trgm")
    op.execute("DROP INDEX IF EXISTS ix_trains_train_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_stations_city_trgm")
    op.execute("DROP INDEX IF EXISTS ix_stations_code_trgm")
    op.execute("DROP INDEX IF EXISTS ix_stations_name_trgm")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
