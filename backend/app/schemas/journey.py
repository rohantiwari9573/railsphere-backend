from pydantic import BaseModel


class JourneyResponse(BaseModel):
    train_number: str
    train_name: str
    route_code: str
    start_time: str
    end_time: str


class JourneySearchResult(BaseModel):
    train_id: int
    train_number: str
    train_name: str
    train_type: str
    route_id: int
    route_code: str
    route_name: str
    departure_time: str | None
    arrival_time: str | None


class StationRouteInfo(BaseModel):
    route_id: int
    route_code: str
    route_name: str
    sequence_number: int
    arrival_time: str | None
    departure_time: str | None


class StationTrainInfo(BaseModel):
    train_id: int
    train_number: str
    train_name: str
    train_type: str
    route_id: int
    route_code: str


class TrainRouteInfo(BaseModel):
    route_id: int
    route_code: str
    route_name: str
    start_time: str
    end_time: str