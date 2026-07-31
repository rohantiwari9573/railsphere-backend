import asyncio
import platform
from contextlib import asynccontextmanager

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from sqlalchemy import text

import app.db.base_models
from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create database tables on application startup.
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# Register all application routes
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to RailSphere 🚆",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


@app.get("/db-health")
async def db_health():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))

    return {
        "database": "connected",
        "result": result.scalar(),
    }