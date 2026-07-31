from __future__ import annotations

from datetime import time
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.route import Route
    from app.models.station import Station


class RouteStation(Base, TimestampMixin):
    __tablename__ = "route_stations"

    __table_args__ = (
        UniqueConstraint(
            "route_id",
            "sequence_number",
            name="uq_route_sequence",
        ),
        UniqueConstraint(
            "route_id",
            "station_id",
            name="uq_route_station",
        ),
        Index(
            "ix_route_station_route_sequence",
            "route_id",
            "sequence_number",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey(
            "routes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    station_id: Mapped[int] = mapped_column(
        ForeignKey(
            "stations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    arrival_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    departure_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    halt_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    distance_from_source: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=0,
        nullable=False,
    )

    route: Mapped[Route] = relationship(
        back_populates="route_stations",
    )

    station: Mapped[Station] = relationship(
        back_populates="route_stations",
    )