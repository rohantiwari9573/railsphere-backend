from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.train import Train


class TrainRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        train: Train,
    ) -> Train:
        self.db.add(train)
        await self.db.commit()
        await self.db.refresh(train)
        return train

    async def bulk_create(
        self,
        trains: list[Train],
    ) -> None:
        self.db.add_all(trains)
        await self.db.commit()

    async def get_by_id(
        self,
        train_id: int,
    ) -> Train | None:
        result = await self.db.execute(
            select(Train).where(
                Train.id == train_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_train_number(
        self,
        train_number: str,
    ) -> Train | None:
        result = await self.db.execute(
            select(Train).where(
                Train.train_number == train_number
            )
        )
        return result.scalar_one_or_none()

    def _search_filter(self, search: str | None):
        if not search:
            return None
        pattern = f"%{search}%"
        return or_(
            Train.train_name.ilike(pattern),
            Train.train_number.ilike(pattern),
        )

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
    ) -> list[Train]:
        query = select(Train)

        search_filter = self._search_filter(search)
        if search_filter is not None:
            query = query.where(search_filter)
            # Best trigram match first (uses the gin_trgm_ops indexes).
            similarity = func.greatest(
                func.similarity(Train.train_name, search),
                func.similarity(Train.train_number, search),
            )
            query = query.order_by(similarity.desc(), Train.train_number)
        else:
            query = query.order_by(Train.train_number)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(Train)

        search_filter = self._search_filter(search)
        if search_filter is not None:
            query = query.where(search_filter)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(
        self,
        train: Train,
    ) -> Train:
        await self.db.commit()
        await self.db.refresh(train)
        return train

    async def delete(
        self,
        train: Train,
    ) -> None:
        await self.db.delete(train)
        await self.db.commit()