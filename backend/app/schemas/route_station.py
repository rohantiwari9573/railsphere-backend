from datetime import time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RouteStationBase(BaseModel):
    route_id: int
    station_id: int
    sequence_number: int
    arrival_time: time | None = None
    departure_time: time | None = None
    halt_minutes: int = 0
    distance_from_source: Decimal = Decimal("0.00")


class RouteStationCreate(RouteStationBase):
    pass


class RouteStationUpdate(BaseModel):
    station_id: int | None = None
    sequence_number: int | None = None
    arrival_time: time | None = None
    departure_time: time | None = None
    halt_minutes: int | None = None
    distance_from_source: Decimal | None = None


class RouteStationResponse(RouteStationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)