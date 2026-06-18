from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base
from app.services.external_clients import (
    faceit_client,
    riot_account_client,
    steam_client,
    valorant_client,
)
from app.services.auto_sync import start_auto_sync, stop_auto_sync
from app.services.cache import ensure_cache_ready, get_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover - simple wiring
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await ensure_cache_ready()
    start_auto_sync()

    yield

    stop_auto_sync()
    await steam_client.aclose()
    await faceit_client.aclose()
    await riot_account_client.aclose()
    await valorant_client.aclose()
    try:
        await get_redis_client().aclose()
    except Exception:
        pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="Statsmec API",
        version="0.1.0",
        description="Backend API for the Statsmec Counter-Strike analytics dashboard.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok"}

