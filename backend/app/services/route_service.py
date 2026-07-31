from app.models.route import Route
from app.repositories.route_repository import RouteRepository
from app.schemas.route import RouteCreate, RouteUpdate


class RouteService:
    def __init__(self, route_repository: RouteRepository):
        self.route_repository = route_repository

    async def create_route(self, route: RouteCreate) -> Route:
        existing_route = await self.route_repository.get_by_route_code(
            route.route_code
        )

        if existing_route:
            raise ValueError("Route with this code already exists.")

        return await self.route_repository.create(route)

    async def get_route(self, route_id: int) -> Route:
        route = await self.route_repository.get_by_id(route_id)

        if not route:
            raise ValueError("Route not found.")

        return route

    async def get_all_routes(self) -> list[Route]:
        return await self.route_repository.get_all()

    async def update_route(
        self,
        route_id: int,
        route_update: RouteUpdate,
    ) -> Route:
        db_route = await self.route_repository.get_by_id(route_id)

        if not db_route:
            raise ValueError("Route not found.")

        if (
            route_update.route_code
            and route_update.route_code != db_route.route_code
        ):
            existing_route = (
                await self.route_repository.get_by_route_code(
                    route_update.route_code
                )
            )

            if existing_route:
                raise ValueError("Route code already exists.")

        return await self.route_repository.update(
            db_route,
            route_update,
        )

    async def delete_route(self, route_id: int) -> None:
        db_route = await self.route_repository.get_by_id(route_id)

        if not db_route:
            raise ValueError("Route not found.")

        await self.route_repository.delete(db_route)