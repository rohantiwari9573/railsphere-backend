from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.station import Station
    from app.models.train import Train
    from app.models.user import User


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    __table_args__ = (
        Index(
            "ix_bookings_train_date_class",
            "train_id",
            "journey_date",
            "travel_class",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    pnr: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    train_id: Mapped[int] = mapped_column(
        ForeignKey("trains.id", ondelete="RESTRICT"), nullable=False
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="RESTRICT"), nullable=False
    )

    source_station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id", ondelete="RESTRICT"), nullable=False
    )

    destination_station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id", ondelete="RESTRICT"), nullable=False
    )

    journey_date: Mapped[date] = mapped_column(Date, nullable=False)

    travel_class: Mapped[str] = mapped_column(String(5), nullable=False)

    # PENDING_PAYMENT, CONFIRMED, PARTIALLY_CONFIRMED, WAITLISTED, CANCELLED
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING_PAYMENT"
    )

    total_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship()
    train: Mapped["Train"] = relationship()
    source_station: Mapped["Station"] = relationship(
        foreign_keys=[source_station_id]
    )
    destination_station: Mapped["Station"] = relationship(
        foreign_keys=[destination_station_id]
    )

    passengers: Mapped[list["Passenger"]] = relationship(
        back_populates="booking",
        cascade="all, delete-orphan",
        order_by="Passenger.id",
    )

    payment: Mapped["Payment | None"] = relationship(
        back_populates="booking",
        cascade="all, delete-orphan",
        uselist=False,
    )


class Passenger(Base, TimestampMixin):
    __tablename__ = "passengers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(1), nullable=False)

    # CONFIRMED, WAITLISTED, CANCELLED
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="WAITLISTED"
    )

    seat_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    coach: Mapped[str | None] = mapped_column(String(10), nullable=True)
    berth_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Assigned at creation time from a per (train, date, class) counter;
    # used to rank waitlisted passengers for promotion on cancellation.
    waitlist_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    booking: Mapped["Booking"] = relationship(back_populates="passengers")


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    transaction_id: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    booking: Mapped["Booking"] = relationship(back_populates="payment")
