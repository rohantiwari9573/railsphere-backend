from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.route_station import RouteStation
    from app.models.schedule import Schedule


class Route(Base, TimestampMixin):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    route_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    route_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    route_stations: Mapped[list["RouteStation"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteStation.sequence_number",
    )

    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
    )