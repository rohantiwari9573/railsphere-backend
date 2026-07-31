from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


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


class Train(Base, TimestampMixin):
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