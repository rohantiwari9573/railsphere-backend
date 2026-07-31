from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import decode_access_token
from app.db.session import get_db

from app.repositories.user_repository import UserRepository
from app.repositories.station_repository import StationRepository
from app.repositories.train_repository import TrainRepository
from app.repositories.route_repository import RouteRepository

from app.services.auth_service import AuthService
from app.services.station_service import StationService
from app.services.train_service import TrainService
from app.services.route_service import RouteService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# -----------------------------
# Repositories
# -----------------------------

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


# -----------------------------
# Services
# -----------------------------

def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


def get_station_service(
    repository: StationRepository = Depends(get_station_repository),
) -> StationService:
    return StationService(repository)


def get_train_service(
    repository: TrainRepository = Depends(get_train_repository),
) -> TrainService:
    return TrainService(repository)


def get_route_service(
    repository: RouteRepository = Depends(get_route_repository),
) -> RouteService:
    return RouteService(repository)


# -----------------------------
# Authentication
# -----------------------------

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