"""add is_admin flag to users

Revision ID: bde6a457fcf1
Revises: 792576969c94
Create Date: 2026-09-08 12:52:13.855151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bde6a457fcf1'
down_revision: Union[str, Sequence[str], None] = '792576969c94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adds users.is_admin, gating the reference-data write endpoints
    (stations/trains/routes/route-stations -- see app/api/dependencies.
    require_admin). Defaults to false for existing and new rows; there's
    no bootstrap admin here on purpose -- promote one with
    scripts/promote_admin.py after this runs.
    """
    op.add_column(
        "users",
        sa.Column(
            "is_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
