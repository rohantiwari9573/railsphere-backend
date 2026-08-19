from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import Route
from app.schemas.route import RouteCreate, RouteUpdate


class RouteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, route: RouteCreate) -> Route:
        db_route = Route(**route.model_dump())

        self.db.add(db_route)
        await self.db.commit()
        await self.db.refresh(db_route)

        return db_route

    async def get_by_id(self, route_id: int) -> Route | None:
        result = await self.db.execute(
            select(Route).where(Route.id == route_id)
        )

        return result.scalar_one_or_none()

    async def get_by_route_code(self, route_code: str) -> Route | None:
        result = await self.db.execute(
            select(Route).where(Route.route_code == route_code)
        )

        return result.scalar_one_or_none()

    def _search_filter(self, search: str | None):
        if not search:
            return None
        pattern = f"%{search}%"
        return or_(
            Route.route_name.ilike(pattern),
            Route.route_code.ilike(pattern),
        )

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
    ) -> list[Route]:
        query = select(Route).order_by(Route.id)

        search_filter = self._search_filter(search)
        if search_filter is not None:
            query = query.where(search_filter)

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(Route)

        search_filter = self._search_filter(search)
        if search_filter is not None:
            query = query.where(search_filter)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(
        self,
        db_route: Route,
        route: RouteUpdate,
    ) -> Route:
        update_data = route.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_route, key, value)

        await self.db.commit()
        await self.db.refresh(db_route)

        return db_route

    async def delete(self, db_route: Route) -> None:
        await self.db.delete(db_route)
        await self.db.commit()