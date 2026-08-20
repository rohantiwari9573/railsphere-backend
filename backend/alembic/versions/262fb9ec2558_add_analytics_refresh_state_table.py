"""add analytics_refresh_state table

Revision ID: 262fb9ec2558
Revises: 78f6f906cc61
Create Date: 2026-08-21 02:19:46.436499

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '262fb9ec2558'
down_revision: Union[str, Sequence[str], None] = '78f6f906cc61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Single-row table tracking when the analytics materialized views
    # were last refreshed, so a client connecting to /ws/analytics
    # mid-cycle can show current state immediately instead of waiting
    # silently for the next NOTIFY.
    op.create_table(
        "analytics_refresh_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "refreshed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.execute(
        "INSERT INTO analytics_refresh_state (id, refreshed_at) "
        "VALUES (1, now())"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("analytics_refresh_state")
