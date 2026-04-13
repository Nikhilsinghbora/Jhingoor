from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import CurrentUser, get_db
from database.models import Meal, UserProfile, Workout

router = APIRouter(tags=["progress"])


class ProgressOut(BaseModel):
    calories_logged: int
    protein_g: int
    calorie_target: int
    protein_target_g: int
    coach_message: str


@router.get("/progress", response_model=ProgressOut)
async def progress(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> ProgressOut:
    today = date.today()
    start = datetime.combine(today, time.min, tzinfo=timezone.utc)
    end = datetime.combine(today, time.max, tzinfo=timezone.utc)

    m_res = await db.execute(
        select(
            func.coalesce(func.sum(Meal.calories), 0),
            func.coalesce(func.sum(Meal.protein_g), 0),
        ).where(Meal.user_id == user.id, Meal.logged_at >= start, Meal.logged_at <= end)
    )
    cal_sum, prot_sum = m_res.one()

    w_res = await db.execute(
        select(func.coalesce(func.sum(Workout.calories), 0)).where(
            Workout.user_id == user.id,
            Workout.starts_at >= start,
            Workout.starts_at <= end,
            Workout.status == "completed",
        )
    )
    workout_cal = int(w_res.scalar_one() or 0)

    calories_logged = int(cal_sum or 0) + workout_cal
    protein_g = int(prot_sum or 0)

    res = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    p = res.scalar_one_or_none()
    cal_target = p.daily_calorie_target if p else 2200
    prot_target = p.daily_protein_target_g if p else 120

    gap = max(0, prot_target - protein_g)
    coach = f"AI COACH: YOU'RE {gap}G PROTEIN FROM YOUR TARGET" if gap else "AI COACH: PROTEIN TARGET HIT FOR TODAY"

    return ProgressOut(
        calories_logged=calories_logged,
        protein_g=protein_g,
        calorie_target=cal_target,
        protein_target_g=prot_target,
        coach_message=coach,
    )
