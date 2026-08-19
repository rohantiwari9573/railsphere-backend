from app.models.route_station import RouteStation
from app.repositories.route_repository import RouteRepository
from app.repositories.route_station_repository import (
    RouteStationRepository,
)
from app.repositories.station_repository import StationRepository
from app.schemas.route_station import (
    RouteStationCreate,
    RouteStationUpdate,
)


class RouteStationService:
    def __init__(
        self,
        route_station_repository: RouteStationRepository,
        route_repository: RouteRepository,
        station_repository: StationRepository,
    ):
        self.route_station_repository = route_station_repository
        self.route_repository = route_repository
        self.station_repository = station_repository

    async def create_route_station(
        self,
        data: RouteStationCreate,
    ) -> RouteStation:

        route = await self.route_repository.get_by_id(
            data.route_id
        )
        if not route:
            raise ValueError("Route not found.")

        station = await self.station_repository.get_by_id(
            data.station_id
        )
        if not station:
            raise ValueError("Station not found.")

        existing_station = await self.route_station_repository.get_by_route_and_station(
            data.route_id,
            data.station_id,
        )
        if existing_station:
            raise ValueError(
                "This station is already part of this route."
            )

        existing_sequence = await self.route_station_repository.get_by_route_and_sequence(
            data.route_id,
            data.sequence_number,
        )
        if existing_sequence:
            raise ValueError(
                "This sequence number is already used on this route."
            )

        route_station = RouteStation(**data.model_dump())

        return await self.route_station_repository.create(
            route_station
        )

    async def get_route_station(
        self,
        route_station_id: int,
    ) -> RouteStation:

        route_station = (
            await self.route_station_repository.get_by_id(
                route_station_id
            )
        )

        if not route_station:
            raise ValueError("Route station not found.")

        return route_station

    async def get_route_stations(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[RouteStation], int]:
        route_stations = await self.route_station_repository.get_all(
            skip=skip, limit=limit
        )
        total = await self.route_station_repository.count()
        return route_stations, total

    async def get_route_stations_by_route(
        self,
        route_id: int,
    ) -> list[RouteStation]:
        return await self.route_station_repository.get_by_route(
            route_id
        )

    async def update_route_station(
        self,
        route_station_id: int,
        data: RouteStationUpdate,
    ) -> RouteStation:

        route_station = (
            await self.route_station_repository.get_by_id(
                route_station_id
            )
        )

        if not route_station:
            raise ValueError("Route station not found.")

        update_data = data.model_dump(exclude_unset=True)

        new_station_id = update_data.get(
            "station_id", route_station.station_id
        )
        new_sequence_number = update_data.get(
            "sequence_number", route_station.sequence_number
        )

        if new_station_id != route_station.station_id:
            existing_station = await self.route_station_repository.get_by_route_and_station(
                route_station.route_id,
                new_station_id,
            )
            if existing_station:
                raise ValueError(
                    "This station is already part of this route."
                )

        if new_sequence_number != route_station.sequence_number:
            existing_sequence = await self.route_station_repository.get_by_route_and_sequence(
                route_station.route_id,
                new_sequence_number,
            )
            if existing_sequence:
                raise ValueError(
                    "This sequence number is already used on this route."
                )

        for key, value in update_data.items():
            setattr(route_station, key, value)

        return await self.route_station_repository.update(
            route_station
        )

    async def delete_route_station(
        self,
        route_station_id: int,
    ):

        route_station = (
            await self.route_station_repository.get_by_id(
                route_station_id
            )
        )

        if not route_station:
            raise ValueError("Route station not found.")

        await self.route_station_repository.delete(
            route_station
        )