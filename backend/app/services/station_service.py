from app.models.station import Station
from app.repositories.station_repository import StationRepository
from app.schemas.station import StationCreate, StationUpdate


class StationService:
    def __init__(
        self,
        repository: StationRepository,
    ):
        self.repository = repository

    async def create_station(
        self,
        station_data: StationCreate,
    ) -> Station:

        existing_station = await self.repository.get_by_code(
            station_data.code
        )

        if existing_station:
            raise ValueError(
                "Station code already exists."
            )

        station = Station(
            code=station_data.code,
            name=station_data.name,
            city=station_data.city,
            state=station_data.state,
        )

        return await self.repository.create(station)

    async def get_all_stations(self):
        return await self.repository.get_all()

    async def get_station(
        self,
        station_id: int,
    ):
        station = await self.repository.get_by_id(
            station_id
        )

        if not station:
            raise ValueError("Station not found.")

        return station

    async def update_station(
        self,
        station_id: int,
        station_data: StationUpdate,
    ):
        station = await self.repository.get_by_id(
            station_id
        )

        if not station:
            raise ValueError("Station not found.")

        update_data = station_data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(station, key, value)

        return await self.repository.update(
            station
        )

    async def delete_station(
        self,
        station_id: int,
    ):
        station = await self.repository.get_by_id(
            station_id
        )

        if not station:
            raise ValueError("Station not found.")

        await self.repository.delete(station)