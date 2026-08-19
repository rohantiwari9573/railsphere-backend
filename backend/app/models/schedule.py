from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.route import Route
    from app.models.train import Train


class Schedule(Base, TimestampMixin):
    __tablename__ = "schedules"

    __table_args__ = (
        UniqueConstraint(
            "train_id",
            "route_id",
            name="uq_schedule_train_route",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    train_id: Mapped[int] = mapped_column(
        ForeignKey(
            "trains.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey(
            "routes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    start_time: Mapped[Time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[Time] = mapped_column(
        Time,
        nullable=False,
    )

    monday: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    tuesday: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    wednesday: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    thursday: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    friday: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    saturday: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    sunday: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    train: Mapped["Train"] = relationship(
        back_populates="schedules",
    )

    route: Mapped["Route"] = relationship(
        back_populates="schedules",
    )