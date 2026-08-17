from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.schedule import Schedule


class Train(Base, TimestampMixin):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    train_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    train_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    train_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    zone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    distance_km: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    return_train_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="train",
        cascade="all, delete-orphan",
    )