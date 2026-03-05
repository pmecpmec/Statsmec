from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


PMEC_STEAM_ID = "76561198245080640"
PMEC_FACEIT_NICKNAME = "pmec"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Statsmec API"
    API_V1_STR: str = "/api/v1"

    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "statsmec"
    POSTGRES_PASSWORD: str = "statsmec"
    POSTGRES_DB: str = "statsmec"

    DATABASE_URL: str | None = None

    REDIS_URL: str = "redis://redis:6379/0"

    STEAM_API_KEY: str | None = None
    FACEIT_API_KEY: str | None = None

    # MongoDB (optional cache)
    MONGODB_URI: str | None = None
    MONGODB_DB_NAME: str = "statsmec"

    # Allstar.gg Partner API
    ALLSTAR_SERVER_API_KEY: str | None = None
    ALLSTAR_PUBLIC_API_KEY: str | None = None

    # CS2 Premier (no public API; optional override)
    PMEC_PREMIER_RATING: int | None = None  # e.g. 18500
    PMEC_PREMIER_COLOR: str | None = None   # optional hex; if unset, derived from rating
    # Optional third-party text endpoint for Premier + Faceit elo
    # e.g. https://api.jakobkristensen.com with output "{{rating}}|{{elo}}"
    PMEC_PREMIER_REMOTE_URL: str | None = None

    BACKEND_CORS_ORIGINS: List[str] = Field(default=["*"])

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def sync_database_uri(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_database_uri(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
