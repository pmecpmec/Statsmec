from fastapi import APIRouter

from app.api.v1.routes import analytics, me, users, valorant


api_router = APIRouter()

api_router.include_router(me.router, prefix="/me", tags=["profile"])
api_router.include_router(valorant.router, prefix="/valorant", tags=["valorant"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
