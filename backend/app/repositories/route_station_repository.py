from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route_station import RouteStation


class RouteStationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        route_station: RouteStation,
    ) -> RouteStation:
        self.db.add(route_station)
        await self.db.commit()
        await self.db.refresh(route_station)
        return route_station

    async def get_all(self) -> list[RouteStation]:
        result = await self.db.execute(
            select(RouteStation).order_by(
                RouteStation.route_id,
                RouteStation.sequence_number,
            )
        )
        return list(result.scalars().all())

    async def get_by_id(
        self,
        route_station_id: int,
    ) -> RouteStation | None:
        result = await self.db.execute(
            select(RouteStation).where(
                RouteStation.id == route_station_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_route(
        self,
        route_id: int,
    ) -> list[RouteStation]:
        result = await self.db.execute(
            select(RouteStation)
            .where(RouteStation.route_id == route_id)
            .order_by(RouteStation.sequence_number)
        )
        return list(result.scalars().all())

    async def get_by_route_and_station(
        self,
        route_id: int,
        station_id: int,
    ) -> RouteStation | None:
        result = await self.db.execute(
            select(RouteStation).where(
                RouteStation.route_id == route_id,
                RouteStation.station_id == station_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_route_and_sequence(
        self,
        route_id: int,
        sequence_number: int,
    ) -> RouteStation | None:
        result = await self.db.execute(
            select(RouteStation).where(
                RouteStation.route_id == route_id,
                RouteStation.sequence_number == sequence_number,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        route_station: RouteStation,
    ) -> RouteStation:
        await self.db.commit()
        await self.db.refresh(route_station)
        return route_station

    async def delete(
        self,
        route_station: RouteStation,
    ):
        await self.db.delete(route_station)
        await self.db.commit()