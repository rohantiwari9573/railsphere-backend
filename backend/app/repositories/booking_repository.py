from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.booking import Booking, Passenger, Payment
from app.models.route_station import RouteStation


def _loaded_booking_query():
    # populate_existing() matters here: a booking already fetched
    # earlier in the same request/session (e.g. an ownership check
    # before a mutation) sits in the identity map with its relationships
    # already resolved. Without this, a later re-fetch after payment/
    # cancellation would keep returning those stale cached relationship
    # values (e.g. `payment=None`) instead of the row we just wrote.
    return (
        select(Booking)
        .options(
            joinedload(Booking.train),
            joinedload(Booking.source_station),
            joinedload(Booking.destination_station),
            selectinload(Booking.passengers),
            selectinload(Booking.payment),
        )
        .execution_options(populate_existing=True)
    )


class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_confirmed(
        self, train_id: int, journey_date: date, travel_class: str
    ) -> int:
        result = await self.db.execute(
            select(func.count(Passenger.id))
            .join(Booking, Booking.id == Passenger.booking_id)
            .where(
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.travel_class == travel_class,
                Passenger.status == "CONFIRMED",
            )
        )
        return result.scalar_one()

    async def count_waitlisted(
        self, train_id: int, journey_date: date, travel_class: str
    ) -> int:
        result = await self.db.execute(
            select(func.count(Passenger.id))
            .join(Booking, Booking.id == Passenger.booking_id)
            .where(
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.travel_class == travel_class,
                Passenger.status == "WAITLISTED",
            )
        )
        return result.scalar_one()

    async def get_confirmed_seat_numbers(
        self, train_id: int, journey_date: date, travel_class: str
    ) -> set[int]:
        result = await self.db.execute(
            select(Passenger.seat_number)
            .join(Booking, Booking.id == Passenger.booking_id)
            .where(
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.travel_class == travel_class,
                Passenger.status == "CONFIRMED",
            )
        )
        return {row[0] for row in result.all()}

    async def next_waitlist_rank(
        self, train_id: int, journey_date: date, travel_class: str
    ) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.max(Passenger.waitlist_rank), 0))
            .join(Booking, Booking.id == Passenger.booking_id)
            .where(
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.travel_class == travel_class,
            )
        )
        return result.scalar_one() + 1

    async def get_min_rank_waitlisted(
        self, train_id: int, journey_date: date, travel_class: str
    ) -> Passenger | None:
        result = await self.db.execute(
            select(Passenger)
            .join(Booking, Booking.id == Passenger.booking_id)
            .where(
                Booking.train_id == train_id,
                Booking.journey_date == journey_date,
                Booking.travel_class == travel_class,
                Passenger.status == "WAITLISTED",
            )
            .order_by(Passenger.waitlist_rank.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_route_segment(
        self, route_id: int, source_station_id: int, destination_station_id: int
    ) -> tuple[RouteStation, RouteStation] | None:
        """
        The two RouteStation rows for the source and destination on a
        given route, used to validate direction and compute the
        partial (not whole-route) travel distance.
        """
        result = await self.db.execute(
            select(RouteStation).where(
                RouteStation.route_id == route_id,
                RouteStation.station_id.in_(
                    [source_station_id, destination_station_id]
                ),
            )
        )
        rows = {row.station_id: row for row in result.scalars().all()}
        source = rows.get(source_station_id)
        destination = rows.get(destination_station_id)
        if source is None or destination is None:
            return None
        return source, destination

    async def get_route_stop_count(self, route_id: int) -> int:
        result = await self.db.execute(
            select(func.count(RouteStation.id)).where(
                RouteStation.route_id == route_id
            )
        )
        return result.scalar_one()

    async def pnr_exists(self, pnr: str) -> bool:
        result = await self.db.execute(
            select(Booking.id).where(Booking.pnr == pnr)
        )
        return result.scalar_one_or_none() is not None

    async def create(self, booking: Booking) -> Booking:
        self.db.add(booking)
        await self.db.commit()
        return await self.get_by_id(booking.id)

    async def get_by_id(self, booking_id: int) -> Booking | None:
        result = await self.db.execute(
            _loaded_booking_query().where(Booking.id == booking_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_by_pnr(self, pnr: str) -> Booking | None:
        result = await self.db.execute(
            _loaded_booking_query().where(Booking.pnr == pnr)
        )
        return result.unique().scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> list[Booking]:
        result = await self.db.execute(
            _loaded_booking_query()
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
        )
        return list(result.unique().scalars().all())

    async def add_payment(self, payment: Payment) -> None:
        self.db.add(payment)
        await self.db.commit()

    async def save(self) -> None:
        await self.db.commit()
