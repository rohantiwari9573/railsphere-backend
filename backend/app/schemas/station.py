from pydantic import BaseModel, ConfigDict


class StationBase(BaseModel):
    code: str
    name: str
    city: str
    state: str


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    city: str | None = None
    state: str | None = None


class StationResponse(StationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)