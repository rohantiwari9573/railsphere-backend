from sqlalchemy import func, or_, select
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

    def _search_filter(self, search: str | None):
        if not search:
            return None
        pattern = f"%{search}%"
        return or_(
            Station.name.ilike(pattern),
            Station.code.ilike(pattern),
            Station.city.ilike(pattern),
        )

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
    ) -> list[Station]:
        query = select(Station)

        search_filter = self._search_filter(search)
        if search_filter is not None:
            query = query.where(search_filter)
            # Best trigram match first (uses the gin_trgm_ops indexes),
            # so "kanpur" surfaces KANPUR CENTRAL before a station whose
            # city merely contains "kanpur" further down alphabetically.
            similarity = func.greatest(
                func.similarity(Station.name, search),
                func.similarity(Station.code, search),
                func.coalesce(
                    func.similarity(Station.city, search), 0.0
                ),
            )
            query = query.order_by(similarity.desc(), Station.id)
        else:
            query = query.order_by(Station.id)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(Station)

        search_filter = self._search_filter(search)
        if search_filter is not None:
            query = query.where(search_filter)

        result = await self.db.execute(query)
        return result.scalar_one()

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