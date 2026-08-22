import asyncio
import logging
import platform
from contextlib import asynccontextmanager

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import settings
from app.graphql.schema import graphql_router
from app.core.http_caching import HttpCachingMiddleware
from app.core.logging_config import configure_logging
from app.core.pg_listen import listen_for_analytics_refresh
from app.core.rate_limit import limiter
from app.core.request_context import set_request_id
from app.core.tracing import configure_tracing
from app.db.database import engine

configure_logging()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.

    Database schema is managed exclusively through Alembic. The
    pg LISTEN task bridges NOTIFYs from AnalyticsRepository.refresh_
    views (which may run in a separate arq worker process) to this
    process's connected /ws/analytics clients.
    """
    listen_task = asyncio.create_task(listen_for_analytics_refresh())
    yield
    listen_task.cancel()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Exposes request counts/latencies/status codes per route at /metrics
# in Prometheus's text format -- point a Prometheus server (or just
# `curl` it) at that endpoint, nothing else to run.
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
configure_tracing(app)
app.add_middleware(HttpCachingMiddleware)

if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = set_request_id(request.headers.get("X-Request-ID"))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(api_router)
app.include_router(graphql_router, prefix="/graphql")


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