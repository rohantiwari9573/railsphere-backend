"""add checked_in_at to bookings

Revision ID: 7d1c4e9a2b30
Revises: bde6a457fcf1
Create Date: 2026-10-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d1c4e9a2b30'
down_revision: Union[str, Sequence[str], None] = 'bde6a457fcf1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Records when a booking's ticket was first validated at boarding
    (see POST /tickets/verify). Null means not yet checked in; the
    column is set once, so a second scan of the same ticket is rejected.
    """
    op.add_column(
        "bookings",
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("bookings", "checked_in_at")
