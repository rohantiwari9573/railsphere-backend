from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession


class BaseImporter(ABC):
    """
    Base class for all dataset importers.
    """

    def __init__(
        self,
        db: AsyncSession,
        dataset_path: str,
    ):
        self.db = db
        self.dataset_path = Path(dataset_path)

    def exists(self) -> bool:
        return self.dataset_path.exists()

    @abstractmethod
    async def import_data(self) -> None:
        """
        Import dataset into database.
        """
        raise NotImplementedError