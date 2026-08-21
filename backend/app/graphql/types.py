from __future__ import annotations

import strawberry

from app.models.route import Route
from app.models.station import Station
from app.models.train import Train


@strawberry.type
class StationType:
    id: int
    code: str
    name: str
    city: str | None
    state: str | None
    zone: str | None
    latitude: float | None
    longitude: float | None
    is_active: bool

    @staticmethod
    def from_model(station: Station) -> "StationType":
        return StationType(
            id=station.id,
            code=station.code,
            name=station.name,
            city=station.city,
            state=station.state,
            zone=station.zone,
            latitude=station.latitude,
            longitude=station.longitude,
            is_active=station.is_active,
        )


@strawberry.type
class TrainType:
    id: int
    train_number: str
    train_name: str
    train_type: str
    zone: str | None
    distance_km: int
    duration_minutes: int
    is_active: bool

    @staticmethod
    def from_model(train: Train) -> "TrainType":
        return TrainType(
            id=train.id,
            train_number=train.train_number,
            train_name=train.train_name,
            train_type=train.train_type,
            zone=train.zone,
            distance_km=train.distance_km,
            duration_minutes=train.duration_minutes,
            is_active=train.is_active,
        )


@strawberry.type
class RouteType:
    id: int
    route_code: str
    route_name: str
    is_active: bool

    @staticmethod
    def from_model(route: Route) -> "RouteType":
        return RouteType(
            id=route.id,
            route_code=route.route_code,
            route_name=route.route_name,
            is_active=route.is_active,
        )
