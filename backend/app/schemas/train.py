from pydantic import BaseModel, ConfigDict, Field


class TrainBase(BaseModel):
    train_number: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Unique train number",
    )

    train_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Train name",
    )

    train_type: str = Field(
        ...,
        max_length=50,
        description="Train type",
    )

    zone: str | None = Field(
        default=None,
        max_length=20,
    )

    distance_km: int = Field(
        default=0,
        ge=0,
    )

    duration_minutes: int = Field(
        default=0,
        ge=0,
    )

    return_train_number: str | None = Field(
        default=None,
        max_length=20,
    )

    is_active: bool = True


class TrainCreate(TrainBase):
    pass


class TrainUpdate(BaseModel):
    train_number: str | None = Field(
        default=None,
        min_length=5,
        max_length=20,
    )

    train_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    train_type: str | None = Field(
        default=None,
        max_length=50,
    )

    zone: str | None = Field(
        default=None,
        max_length=20,
    )

    distance_km: int | None = Field(
        default=None,
        ge=0,
    )

    duration_minutes: int | None = Field(
        default=None,
        ge=0,
    )

    return_train_number: str | None = Field(
        default=None,
        max_length=20,
    )

    is_active: bool | None = None


class TrainResponse(TrainBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )