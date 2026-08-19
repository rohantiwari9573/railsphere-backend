from pydantic import BaseModel


class NetworkOverview(BaseModel):
    total_stations: int
    total_trains: int
    total_routes: int
    total_route_stations: int
    total_schedules: int
    avg_stations_per_route: float


class TopStation(BaseModel):
    station_id: int
    name: str
    code: str
    route_count: int


class TopRoute(BaseModel):
    route_id: int
    route_code: str
    route_name: str
    stop_count: int


class TrainTypeCount(BaseModel):
    train_type: str
    count: int
