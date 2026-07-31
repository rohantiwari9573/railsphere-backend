from pydantic import BaseModel, ConfigDict, Field

from app.models.train import TrainStatus, TrainType


class TrainBase(BaseModel):
    train_number: str = Field(
        ...,
        min_length=5,
        max_length=10,
        description="Unique train number",
    )

    train_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Train name",
    )

    train_type: TrainType

    total_coaches: int = Field(
        ...,
        gt=0,
        description="Total number of coaches",
    )

    status: TrainStatus = TrainStatus.ACTIVE


class TrainCreate(TrainBase):
    pass


class TrainUpdate(BaseModel):
    train_number: str | None = Field(
        default=None,
        min_length=5,
        max_length=10,
    )

    train_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    train_type: TrainType | None = None

    total_coaches: int | None = Field(
        default=None,
        gt=0,
    )

    status: TrainStatus | None = None


class TrainResponse(TrainBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )