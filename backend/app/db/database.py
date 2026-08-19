from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    # SQL statement logging is controlled via the "sqlalchemy.engine"
    # logger (see app/core/logging_config.py), not the echo flag --
    # echo=True installs its own handler and double-prints every line
    # alongside the app's logging config.
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)