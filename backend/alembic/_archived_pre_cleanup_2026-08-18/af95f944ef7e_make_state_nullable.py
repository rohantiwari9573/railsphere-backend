"""make state nullable"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "YOUR_NEW_REVISION_ID"
down_revision: Union[str, Sequence[str], None] = "175153bb110c"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.alter_column(
        "stations",
        "state",
        existing_type=sa.String(length=100),
        nullable=True,
    )


def downgrade() -> None:

    op.alter_column(
        "stations",
        "state",
        existing_type=sa.String(length=100),
        nullable=False,
    )