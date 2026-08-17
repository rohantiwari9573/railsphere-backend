from app.models.train import Train
from app.repositories.train_repository import TrainRepository
from app.schemas.train import (
    TrainCreate,
    TrainUpdate,
)


class TrainService:
    def __init__(
        self,
        repository: TrainRepository,
    ):
        self.repository = repository

    async def create_train(
        self,
        train_data: TrainCreate,
    ) -> Train:

        existing_train = (
            await self.repository.get_by_train_number(
                train_data.train_number
            )
        )

        if existing_train:
            raise ValueError(
                "Train number already exists."
            )

        train = Train(
            train_number=train_data.train_number,
            train_name=train_data.train_name,
            train_type=train_data.train_type,
            zone=train_data.zone,
            distance_km=train_data.distance_km,
            duration_minutes=train_data.duration_minutes,
            return_train_number=train_data.return_train_number,
            is_active=train_data.is_active,
        )

        return await self.repository.create(
            train
        )

    async def get_train(
        self,
        train_id: int,
    ) -> Train:

        train = await self.repository.get_by_id(
            train_id
        )

        if not train:
            raise ValueError(
                "Train not found."
            )

        return train

    async def get_all_trains(
        self,
    ) -> list[Train]:
        return await self.repository.get_all()

    async def update_train(
        self,
        train_id: int,
        train_data: TrainUpdate,
    ) -> Train:

        train = await self.repository.get_by_id(
            train_id
        )

        if not train:
            raise ValueError(
                "Train not found."
            )

        update_data = train_data.model_dump(
            exclude_unset=True
        )

        if (
            "train_number" in update_data
            and update_data["train_number"]
            != train.train_number
        ):
            existing_train = (
                await self.repository.get_by_train_number(
                    update_data["train_number"]
                )
            )

            if existing_train:
                raise ValueError(
                    "Train number already exists."
                )

        for key, value in update_data.items():
            setattr(train, key, value)

        return await self.repository.update(
            train
        )

    async def delete_train(
        self,
        train_id: int,
    ) -> None:

        train = await self.repository.get_by_id(
            train_id
        )

        if not train:
            raise ValueError(
                "Train not found."
            )

        await self.repository.delete(
            train
        )