from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PMEC_STEAM_ID = "76561198245080640"
PMEC_FACEIT_NICKNAME = "pmec"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Statsmec API"
    API_V1_STR: str = "/api/v1"
    # "development" = verbose setup hints in JSON responses; "production" = safe messages for public APIs.
    APP_ENV: str = "production"

    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "statsmec"
    POSTGRES_PASSWORD: str = "statsmec"
    POSTGRES_DB: str = "statsmec"

    DATABASE_URL: str | None = None

    REDIS_URL: str = "redis://redis:6379/0"

    STEAM_API_KEY: str | None = None
    FACEIT_API_KEY: str | None = None

    # Riot Games API (Valorant / account-v1). Use header X-Riot-Token (development keys are RGAPI-...).
    RIOT_API_KEY: str | None = None
    # Regional routing for account-v1: americas | europe | asia
    RIOT_ROUTING_REGION: str = "europe"
    # Valorant game endpoints (match list, etc.): na | latam | br | eu | ap | kr
    RIOT_VAL_SHARD: str = "eu"
    # Default Riot ID for /me/valorant when query params omitted (GameName + tag, e.g. name "pmec" tag "EUW")
    RIOT_GAME_NAME: str | None = None
    RIOT_TAG_LINE: str | None = None
    # Multiple Valorant accounts: comma-separated Riot IDs "name#tag,name#tag" (overrides single pair when set)
    RIOT_RIOT_IDS: str | None = None

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

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

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

    @property
    def valorant_riot_id_pairs(self) -> list[tuple[str, str]]:
        """(game_name, tag_line) for each configured Valorant Riot ID."""
        pairs: list[tuple[str, str]] = []
        raw = (self.RIOT_RIOT_IDS or "").strip()
        if raw:
            for part in raw.split(","):
                part = part.strip()
                if "#" not in part:
                    continue
                name, _, tag = part.partition("#")
                name, tag = name.strip(), tag.strip()
                if name and tag:
                    pairs.append((name, tag))
        if not pairs:
            gn = (self.RIOT_GAME_NAME or "").strip()
            tg = (self.RIOT_TAG_LINE or "").strip()
            if gn and tg:
                pairs.append((gn, tg))
        return pairs

    @property
    def dev_hints_in_api(self) -> bool:
        return (self.APP_ENV or "").strip().lower() in ("development", "dev", "local")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
