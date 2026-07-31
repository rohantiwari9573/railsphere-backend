from sqlalchemy import select
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

    async def get_by_id(
        self,
        train_id: int,
    ) -> Train | None:
        result = await self.db.execute(
            select(Train).where(Train.id == train_id)
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

    async def get_all(self) -> list[Train]:
        result = await self.db.execute(
            select(Train)
        )
        return list(result.scalars().all())

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