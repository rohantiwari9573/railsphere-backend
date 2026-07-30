from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.station import Station


class StationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, station: Station) -> Station:
        self.db.add(station)
        await self.db.commit()
        await self.db.refresh(station)
        return station

    async def get_all(self) -> list[Station]:
        result = await self.db.execute(
            select(Station).order_by(Station.id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, station_id: int) -> Station | None:
        result = await self.db.execute(
            select(Station).where(
                Station.id == station_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Station | None:
        result = await self.db.execute(
            select(Station).where(
                Station.code == code
            )
        )
        return result.scalar_one_or_none()

    async def update(self, station: Station) -> Station:
        await self.db.commit()
        await self.db.refresh(station)
        return station

    async def delete(self, station: Station):
        await self.db.delete(station)
        await self.db.commit()