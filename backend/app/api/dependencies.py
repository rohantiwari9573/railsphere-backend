from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import decode_access_token
from app.db.session import get_db

from app.repositories.user_repository import UserRepository
from app.repositories.station_repository import StationRepository

from app.services.auth_service import AuthService
from app.services.station_service import StationService

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