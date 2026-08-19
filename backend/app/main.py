import asyncio
import logging
import platform
from contextlib import asynccontextmanager

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.db.database import engine

configure_logging()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.

    Database schema is managed exclusively through Alembic.
    """
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled exception on %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


@app.get("/")
async def root():
    return {
        "message": "Welcome to RailSphere 🚆",
        "version": settings.APP_VERSION,
    }


@app.get("/db-health")
async def db_health():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))

    return {
        "database": "connected",
        "result": result.scalar(),
    }