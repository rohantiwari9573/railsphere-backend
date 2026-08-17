"""upgrade station model

Revision ID: 175153bb110c
Revises: 74c143295f15
Create Date: 2026-08-03 21:09:49.250111

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "175153bb110c"
down_revision: Union[str, Sequence[str], None] = "74c143295f15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "stations",
        sa.Column(
            "zone",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.add_column(
        "stations",
        sa.Column(
            "address",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "stations",
        sa.Column(
            "latitude",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "stations",
        sa.Column(
            "longitude",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "stations",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.alter_column(
        "stations",
        "name",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.String(length=150),
        existing_nullable=False,
    )

    op.alter_column(
        "stations",
        "city",
        existing_type=sa.VARCHAR(length=100),
        nullable=True,
    )

    op.create_index(
        op.f("ix_stations_name"),
        "stations",
        ["name"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_stations_name"),
        table_name="stations",
    )

    op.alter_column(
        "stations",
        "city",
        existing_type=sa.VARCHAR(length=100),
        nullable=False,
    )

    op.alter_column(
        "stations",
        "name",
        existing_type=sa.String(length=150),
        type_=sa.VARCHAR(length=100),
        existing_nullable=False,
    )

    op.drop_column("stations", "is_active")
    op.drop_column("stations", "longitude")
    op.drop_column("stations", "latitude")
    op.drop_column("stations", "address")
    op.drop_column("stations", "zone")