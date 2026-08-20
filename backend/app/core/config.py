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