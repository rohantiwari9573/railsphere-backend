from collections.abc import AsyncGenerator

from app.db.database import engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session