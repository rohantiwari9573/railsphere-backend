from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str
    APP_VERSION: str

    DEBUG: bool

    HOST: str
    PORT: int

    # Database
    DATABASE_URL: str

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS: comma-separated list of allowed origins, e.g.
    # "http://localhost:5173,https://railsphere.example.com"
    CORS_ORIGINS: str = ""

    # Redis: used for response caching (app/core/cache.py) and as the
    # arq job queue's broker (app/worker.py). Optional -- leave empty
    # to run without Redis; caching then silently no-ops and the
    # scheduled materialized-view refresh must be run manually via
    # scripts/refresh_analytics_views.py instead.
    REDIS_URL: str = ""

    # OpenTelemetry: base URL of an OTLP/HTTP collector (e.g.
    # "http://jaeger:4318" in docker-compose). Optional -- leave empty
    # to run without tracing; no instrumentation or exporter is set up
    # at all in that case, so there's no cost on a memory-constrained
    # instance until a collector is actually configured.
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""

    # Fernet key used to encrypt sensitive columns at rest (currently
    # just User.email) -- generate one with:
    # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # Required (not optional/fail-open like REDIS_URL): without it,
    # nothing that touches an encrypted column can run at all.
    DATA_ENCRYPTION_KEY: str = ""

    # SQLAlchemy connection pool, per engine instance. There's one engine
    # per process -- 2 gunicorn workers + 1 arq worker in production --
    # so the worst case is (DB_POOL_SIZE + DB_POOL_MAX_OVERFLOW) * 3
    # connections. Defaults are deliberately small: the production
    # instance is a t3.micro (1GB RAM) running Postgres natively
    # alongside the app, and each Postgres connection has real memory
    # overhead. 3 + 2 = 5 per engine, 15 total worst case, comfortably
    # under Postgres's default max_connections=100.
    DB_POOL_SIZE: int = 3
    DB_POOL_MAX_OVERFLOW: int = 2
    # Recycle connections periodically so a connection that's been idle
    # long enough to be dropped by the server/a NAT/firewall in between
    # isn't handed back out already-dead. pool_pre_ping also guards
    # against this per-checkout, but recycling avoids paying that
    # extra round-trip on every use.
    DB_POOL_RECYCLE_SECONDS: int = 1800

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()