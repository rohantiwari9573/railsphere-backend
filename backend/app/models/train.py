from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TrainType(str, Enum):
    EXPRESS = "EXPRESS"
    SUPERFAST = "SUPERFAST"
    PASSENGER = "PASSENGER"
    RAJDHANI = "RAJDHANI"
    SHATABDI = "SHATABDI"
    VANDE_BHARAT = "VANDE_BHARAT"
    DURONTO = "DURONTO"
    GARIB_RATH = "GARIB_RATH"


class TrainStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"


class Train(Base):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    train_number: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
    )

    train_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    train_type: Mapped[TrainType] = mapped_column(
        SqlEnum(TrainType),
        nullable=False,
    )

    total_coaches: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[TrainStatus] = mapped_column(
        SqlEnum(TrainStatus),
        default=TrainStatus.ACTIVE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )