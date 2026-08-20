import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:RoHaN999@localhost:5432/railsphere_test",
)

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import fakeredis

from app.api.dependencies import get_cache
from app.core.cache import Cache
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.main import app

test_engine = create_async_engine(settings.DATABASE_URL)

# The rate limiter's storage is in-memory and shared across the whole
# process, so without this, enough tests hitting the same endpoint
# (e.g. auth login/register, capped at 5/minute) would eventually
# start failing with 429s purely from test-suite volume, not from
# anything actually wrong with the app.
limiter.enabled = False


@pytest_asyncio.fixture
async def db_session():
    """
    Runs each test inside an outer transaction that's always rolled
    back, so tests never leave data behind regardless of order.
    App code calls session.commit() directly (no savepoints of its
    own), so join_transaction_mode="create_savepoint" is required --
    it turns those commit() calls into savepoint releases instead of
    ending the outer transaction.
    """
    async with test_engine.connect() as conn:
        trans = await conn.begin()

        session_factory = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_factory() as session:
            yield session

        await trans.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def fake_redis():
    client = fakeredis.FakeAsyncRedis(decode_responses=True)
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def cached_client(client, fake_redis):
    """
    Same client as `client`, but backed by a real (in-memory, fake)
    Redis instead of the no-op Cache(None) every other test gets.
    Only use this for tests that specifically exercise caching --
    everything else should see fresh data on every request.
    """
    app.dependency_overrides[get_cache] = lambda: Cache(fake_redis)
    yield client


@pytest.fixture(autouse=True, scope="session")
def _guard_against_real_database():
    if "railsphere_test" not in settings.DATABASE_URL:
        raise RuntimeError(
            "Tests must run against railsphere_test, not "
            f"{settings.DATABASE_URL!r}. Refusing to continue."
        )
