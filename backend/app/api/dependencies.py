from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import Cache, get_redis_client
from app.core.jwt import decode_access_token
from app.db.session import get_db

from app.repositories.user_repository import UserRepository
from app.repositories.station_repository import StationRepository
from app.repositories.train_repository import TrainRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.route_station_repository import (
    RouteStationRepository,
)
from app.repositories.journey_repository import JourneyRepository
from app.repositories.analytics_repository import AnalyticsRepository

from app.services.auth_service import AuthService
from app.services.station_service import StationService
from app.services.train_service import TrainService
from app.services.route_service import RouteService
from app.services.route_station_service import (
    RouteStationService,
)
from app.services.journey_service import JourneyService
from app.services.analytics_service import AnalyticsService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_cache() -> Cache:
    return Cache(get_redis_client())


# ------------------------------------------------
# Repositories
# ------------------------------------------------

def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(db)


def get_station_repository(
    db: AsyncSession = Depends(get_db),
) -> StationRepository:
    return StationRepository(db)


def get_train_repository(
    db: AsyncSession = Depends(get_db),
) -> TrainRepository:
    return TrainRepository(db)


def get_route_repository(
    db: AsyncSession = Depends(get_db),
) -> RouteRepository:
    return RouteRepository(db)


def get_route_station_repository(
    db: AsyncSession = Depends(get_db),
) -> RouteStationRepository:
    return RouteStationRepository(db)


def get_journey_repository(
    db: AsyncSession = Depends(get_db),
) -> JourneyRepository:
    return JourneyRepository(db)


def get_analytics_repository(
    db: AsyncSession = Depends(get_db),
) -> AnalyticsRepository:
    return AnalyticsRepository(db)


# ------------------------------------------------
# Services
# ------------------------------------------------

def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


def get_station_service(
    repository: StationRepository = Depends(get_station_repository),
    cache: Cache = Depends(get_cache),
) -> StationService:
    return StationService(repository, cache)


def get_train_service(
    repository: TrainRepository = Depends(get_train_repository),
    cache: Cache = Depends(get_cache),
) -> TrainService:
    return TrainService(repository, cache)


def get_route_service(
    repository: RouteRepository = Depends(get_route_repository),
) -> RouteService:
    return RouteService(repository)


def get_route_station_service(
    route_station_repository: RouteStationRepository = Depends(
        get_route_station_repository
    ),
    route_repository: RouteRepository = Depends(
        get_route_repository
    ),
    station_repository: StationRepository = Depends(
        get_station_repository
    ),
) -> RouteStationService:
    return RouteStationService(
        route_station_repository,
        route_repository,
        station_repository,
    )


def get_journey_service(
    repository: JourneyRepository = Depends(
        get_journey_repository,
    ),
) -> JourneyService:
    return JourneyService(repository)


def get_analytics_service(
    repository: AnalyticsRepository = Depends(
        get_analytics_repository,
    ),
    cache: Cache = Depends(get_cache),
) -> AnalyticsService:
    return AnalyticsService(repository, cache)


# ------------------------------------------------
# Authentication
# ------------------------------------------------

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repository: UserRepository = Depends(get_user_repository),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    user = await repository.get_by_id(int(user_id))

    if user is None:
        raise credentials_exception

    return user