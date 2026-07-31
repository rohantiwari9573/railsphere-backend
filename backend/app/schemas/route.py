from pydantic import BaseModel, ConfigDict, Field


class RouteBase(BaseModel):
    route_code: str = Field(
        ...,
        min_length=3,
        max_length=20,
        examples=["NDLS-LKO"],
    )

    route_name: str = Field(
        ...,
        min_length=3,
        max_length=150,
        examples=["New Delhi - Lucknow"],
    )

    is_active: bool = True


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    route_code: str | None = Field(
        default=None,
        min_length=3,
        max_length=20,
    )

    route_name: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    is_active: bool | None = None


class RouteResponse(RouteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)