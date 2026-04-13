from datetime import date, datetime, time, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import CurrentUser, get_db
from database.models import Meal, UserProfile, WeeklyIntensityPoint, Workout

router = APIRouter(tags=["activity"])


class TimelineItemOut(BaseModel):
    id: str
    kind: str
    time_label: str
    title: str
    subtitle: str | None
    status: str | None
    accent: str | None
    calories: int | None = None
    protein_g: int | None = None
    carbs_g: int | None = None
    fats_g: int | None = None
    avg_hr: int | None = None
    sets_count: int | None = None


class ActivityStreamOut(BaseModel):
    date: date
    items: list[TimelineItemOut]


class WorkoutCreate(BaseModel):
    workout_type: str = Field(..., max_length=120)
    duration_min: int = Field(default=0, ge=0, le=24 * 60)
    intensity: int = Field(default=5, ge=1, le=10)
    calories: int = Field(default=0, ge=0)
    avg_hr: int | None = None
    sets_count: int | None = None
    title: str | None = Field(None, max_length=200)
    subtitle: str | None = None


class MealCreate(BaseModel):
    name: str = Field(..., max_length=200)
    calories: int = Field(ge=0, default=0)
    protein_g: int = Field(ge=0, default=0)
    carbs_g: int = Field(ge=0, default=0)
    fats_g: int = Field(ge=0, default=0)


class WeeklyIntensityOut(BaseModel):
    week_start: date
    points: list[dict]


class NextWorkoutOut(BaseModel):
    title: str | None


def _local_day_bounds(d: date) -> tuple[datetime, datetime]:
    start = datetime.combine(d, time.min, tzinfo=timezone.utc)
    end = datetime.combine(d, time.max, tzinfo=timezone.utc)
    return start, end


@router.get("/activity-stream", response_model=ActivityStreamOut)
async def activity_stream(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    stream_date: date = Query(alias="date", default_factory=date.today),
) -> ActivityStreamOut:
    start, end = _local_day_bounds(stream_date)
    w_res = await db.execute(
        select(Workout).where(Workout.user_id == user.id, Workout.starts_at >= start, Workout.starts_at <= end)
    )
    m_res = await db.execute(
        select(Meal).where(Meal.user_id == user.id, Meal.logged_at >= start, Meal.logged_at <= end)
    )
    workouts = list(w_res.scalars().all())
    meals = list(m_res.scalars().all())

    combined: list[tuple[datetime, TimelineItemOut]] = []
    for w in workouts:
        t = w.starts_at.astimezone(timezone.utc)
        status = w.status.upper() if w.status == "completed" else w.status
        combined.append(
            (
                t,
                TimelineItemOut(
                    id=str(w.id),
                    kind="workout",
                    time_label=t.strftime("%I:%M %p").lstrip("0"),
                    title=w.title or w.workout_type,
                    subtitle=w.subtitle,
                    status=status,
                    accent="lime" if w.status == "completed" else "muted",
                    calories=w.calories,
                    avg_hr=w.avg_hr,
                    sets_count=w.sets_count,
                ),
            )
        )
    for m in meals:
        t = m.logged_at.astimezone(timezone.utc)
        combined.append(
            (
                t,
                TimelineItemOut(
                    id=str(m.id),
                    kind="meal",
                    time_label=t.strftime("%I:%M %p").lstrip("0"),
                    title=m.name,
                    subtitle=None,
                    status=None,
                    accent="teal",
                    calories=m.calories,
                    protein_g=m.protein_g,
                    carbs_g=m.carbs_g,
                    fats_g=m.fats_g,
                ),
            )
        )
    combined.sort(key=lambda x: x[0])
    return ActivityStreamOut(date=stream_date, items=[c[1] for c in combined])


@router.post("/workouts", status_code=201)
async def create_workout(
    body: WorkoutCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    w = Workout(
        id=uuid4(),
        user_id=user.id,
        workout_type=body.workout_type,
        duration_min=body.duration_min,
        intensity=body.intensity,
        calories=body.calories,
        avg_hr=body.avg_hr,
        sets_count=body.sets_count,
        title=body.title or body.workout_type,
        subtitle=body.subtitle,
        status="completed",
    )
    db.add(w)
    await db.commit()
    return {"id": str(w.id)}


@router.post("/meals", status_code=201)
async def create_meal(
    body: MealCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    m = Meal(
        id=uuid4(),
        user_id=user.id,
        name=body.name,
        calories=body.calories,
        protein_g=body.protein_g,
        carbs_g=body.carbs_g,
        fats_g=body.fats_g,
    )
    db.add(m)
    await db.commit()
    return {"id": str(m.id)}


@router.get("/activity/weekly-intensity", response_model=WeeklyIntensityOut)
async def weekly_intensity(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> WeeklyIntensityOut:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    res = await db.execute(
        select(WeeklyIntensityPoint).where(
            WeeklyIntensityPoint.user_id == user.id, WeeklyIntensityPoint.week_start == week_start
        )
    )
    pts = sorted(res.scalars().all(), key=lambda x: x.day_index)
    return WeeklyIntensityOut(
        week_start=week_start,
        points=[{"day_index": p.day_index, "value": p.value} for p in pts],
    )


@router.get("/workout/next", response_model=NextWorkoutOut)
async def next_workout(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> NextWorkoutOut:
    res = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    p = res.scalar_one_or_none()
    return NextWorkoutOut(title=p.next_workout_title if p else None)
