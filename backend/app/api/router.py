from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.station import router as station_router
from app.api.routes.train import router as train_router
from app.api.routes.route import router as route_router
from app.api.routes.route_station import (
    router as route_station_router,
)
from app.api.routes.journey import (
    router as journey_router,
)
from app.api.routes.analytics import (
    router as analytics_router,
)
from app.api.routes.booking import router as booking_router
from app.api.routes.ws import router as ws_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(station_router)
api_router.include_router(train_router)
api_router.include_router(route_router)
api_router.include_router(route_station_router)
api_router.include_router(journey_router)
api_router.include_router(analytics_router)
api_router.include_router(booking_router)
api_router.include_router(ws_router)