import strawberry
from fastapi import Depends
from strawberry.fastapi import GraphQLRouter

from app.api.dependencies import (
    get_route_service,
    get_station_service,
    get_train_service,
)
from app.graphql.types import RouteType, StationType, TrainType
from app.services.route_service import RouteService
from app.services.station_service import StationService
from app.services.train_service import TrainService

_MAX_LIMIT = 50


async def get_context(
    station_service: StationService = Depends(get_station_service),
    train_service: TrainService = Depends(get_train_service),
    route_service: RouteService = Depends(get_route_service),
) -> dict:
    return {
        "station_service": station_service,
        "train_service": train_service,
        "route_service": route_service,
    }


@strawberry.type
class Query:
    @strawberry.field(description="A single station by id, or null if not found.")
    async def station(self, info: strawberry.Info, id: int) -> StationType | None:
        service: StationService = info.context["station_service"]
        try:
            station = await service.get_station(id)
        except ValueError:
            return None
        return StationType.from_model(station)

    @strawberry.field(description="Search/paginate stations.")
    async def stations(
        self,
        info: strawberry.Info,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[StationType]:
        service: StationService = info.context["station_service"]
        stations, _ = await service.get_all_stations(
            skip=offset, limit=min(limit, _MAX_LIMIT), search=search
        )
        return [StationType.from_model(s) for s in stations]

    @strawberry.field(description="A single train by id, or null if not found.")
    async def train(self, info: strawberry.Info, id: int) -> TrainType | None:
        service: TrainService = info.context["train_service"]
        try:
            train = await service.get_train(id)
        except ValueError:
            return None
        return TrainType.from_model(train)

    @strawberry.field(description="Search/paginate trains.")
    async def trains(
        self,
        info: strawberry.Info,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[TrainType]:
        service: TrainService = info.context["train_service"]
        trains, _ = await service.get_all_trains(
            skip=offset, limit=min(limit, _MAX_LIMIT), search=search
        )
        return [TrainType.from_model(t) for t in trains]

    @strawberry.field(description="A single route by id, or null if not found.")
    async def route(self, info: strawberry.Info, id: int) -> RouteType | None:
        service: RouteService = info.context["route_service"]
        try:
            route = await service.get_route(id)
        except ValueError:
            return None
        return RouteType.from_model(route)

    @strawberry.field(description="Search/paginate routes.")
    async def routes(
        self,
        info: strawberry.Info,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RouteType]:
        service: RouteService = info.context["route_service"]
        routes, _ = await service.get_all_routes(
            skip=offset, limit=min(limit, _MAX_LIMIT), search=search
        )
        return [RouteType.from_model(r) for r in routes]


schema = strawberry.Schema(query=Query)

graphql_router = GraphQLRouter(schema, context_getter=get_context)
