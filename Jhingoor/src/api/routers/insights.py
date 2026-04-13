from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import CurrentUser, get_db
from database.models import UserProfile

router = APIRouter(tags=["insights"])


class DailyInsightOut(BaseModel):
    insight: str | None


@router.get("/insights/daily", response_model=DailyInsightOut)
async def daily_insight(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> DailyInsightOut:
    res = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    p = res.scalar_one_or_none()
    return DailyInsightOut(insight=p.insight_body if p else None)
