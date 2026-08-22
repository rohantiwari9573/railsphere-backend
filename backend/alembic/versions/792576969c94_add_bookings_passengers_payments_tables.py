"""add bookings passengers payments tables

Revision ID: 792576969c94
Revises: f702a1d0fc9c
Create Date: 2026-08-23 01:03:29.982328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '792576969c94'
down_revision: Union[str, Sequence[str], None] = 'f702a1d0fc9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('bookings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pnr', sa.String(length=10), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('train_id', sa.Integer(), nullable=False),
    sa.Column('route_id', sa.Integer(), nullable=False),
    sa.Column('source_station_id', sa.Integer(), nullable=False),
    sa.Column('destination_station_id', sa.Integer(), nullable=False),
    sa.Column('journey_date', sa.Date(), nullable=False),
    sa.Column('travel_class', sa.String(length=5), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('total_fare', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['destination_station_id'], ['stations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['source_station_id'], ['stations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['train_id'], ['trains.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_pnr'), 'bookings', ['pnr'], unique=True)
    op.create_index('ix_bookings_train_date_class', 'bookings', ['train_id', 'journey_date', 'travel_class'], unique=False)
    op.create_table('passengers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('gender', sa.String(length=1), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('seat_number', sa.Integer(), nullable=True),
    sa.Column('coach', sa.String(length=10), nullable=True),
    sa.Column('berth_type', sa.String(length=20), nullable=True),
    sa.Column('waitlist_rank', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_passengers_id'), 'passengers', ['id'], unique=False)
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('method', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('transaction_id', sa.String(length=30), nullable=False),
    sa.Column('paid_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('booking_id'),
    sa.UniqueConstraint('transaction_id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_passengers_id'), table_name='passengers')
    op.drop_table('passengers')
    op.drop_index('ix_bookings_train_date_class', table_name='bookings')
    op.drop_index(op.f('ix_bookings_pnr'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_table('bookings')
