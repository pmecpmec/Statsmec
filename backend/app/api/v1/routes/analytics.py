from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics import compute_full_analytics
from app.services.cache import cached


router = APIRouter()


@router.get("/users/{user_id}", response_model=AnalyticsResponse)
async def get_user_analytics(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> AnalyticsResponse:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    async def _compute() -> dict:
        analytics = await compute_full_analytics(db, user_id=user.id, rank=user.rank)
        return analytics.model_dump()

    data = await cached(f"analytics:user:{user_id}", 300, _compute)
    return AnalyticsResponse.model_validate(data)

