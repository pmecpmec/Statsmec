from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base
from app.services.external_clients import faceit_client, steam_client
from app.services.cache import get_redis_client


def create_app() -> FastAPI:
    app = FastAPI(
        title="Statsmec API",
        version="0.1.0",
        description="Backend API for the Statsmec Counter-Strike analytics dashboard.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup() -> None:  # pragma: no cover - simple wiring
        # Ensure database schema exists for local/dev usage.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Touch Redis client so connection pool is ready.
        _ = get_redis_client()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:  # pragma: no cover - simple wiring
        await steam_client.aclose()
        await faceit_client.aclose()
        await get_redis_client().aclose()

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok"}

