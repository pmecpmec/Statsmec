from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Statsmec API"
    API_V1_STR: str = "/api/v1"

    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "statsmec"
    POSTGRES_PASSWORD: str = "statsmec"
    POSTGRES_DB: str = "statsmec"

    REDIS_URL: str = "redis://redis:6379/0"

    STEAM_API_KEY: str | None = None
    FACEIT_API_KEY: str | None = None

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(default_factory=list)

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def sync_database_uri(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_database_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

