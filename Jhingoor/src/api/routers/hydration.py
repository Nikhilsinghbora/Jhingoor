from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import CurrentUser, get_db
from database.models import HydrationDay, UserProfile

router = APIRouter(tags=["hydration"])


class HydrationLogIn(BaseModel):
    amount_ml: int = Field(gt=0, le=5000)


class HydrationOut(BaseModel):
    total_ml: int
    target_ml: int


@router.post("/hydration/log", response_model=HydrationOut)
async def log_hydration(
    body: HydrationLogIn,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> HydrationOut:
    today = date.today()
    res = await db.execute(
        select(HydrationDay).where(HydrationDay.user_id == user.id, HydrationDay.log_date == today)
    )
    row = res.scalar_one_or_none()
    if row:
        row.total_ml += body.amount_ml
    else:
        row = HydrationDay(user_id=user.id, log_date=today, total_ml=body.amount_ml)
        db.add(row)

    p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    p = p_res.scalar_one_or_none()
    if p:
        p.hydration_current_ml = row.total_ml

    await db.commit()
    target = p.hydration_target_ml if p else 3500
    return HydrationOut(total_ml=row.total_ml, target_ml=target)
