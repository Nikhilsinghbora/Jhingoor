from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import CurrentUser, get_db
from database.models import (
    ActivityMixStat,
    BiometricSnapshot,
    User,
    UserProfile,
    WeightEntry,
)

router = APIRouter(prefix="/user", tags=["user"])


class ProfileOut(BaseModel):
    email: EmailStr
    display_name: str
    bio: str | None
    level: int
    membership_tier: str


class GoalsOut(BaseModel):
    target_weight_kg: float | None
    daily_steps_target: int
    daily_protein_target_g: int
    daily_calorie_target: int
    goal_progress_pct: float


class IntegrationItem(BaseModel):
    id: str
    title: str
    description: str
    enabled: bool


class IntegrationsOut(BaseModel):
    items: list[IntegrationItem]


class SubscriptionOut(BaseModel):
    plan: str | None
    price_display: str | None
    next_billing_date: date | None


class DashboardOut(BaseModel):
    active_energy_kcal: int
    steps: int
    sleep_minutes: int
    insight: str | None
    hydration_target_ml: int
    hydration_current_ml: int
    next_workout_title: str | None
    biometrics: list[dict]


class MomentumOut(BaseModel):
    status: str | None
    bmi: float | None
    weight_change_month_kg: float | None
    regional_rank_label: str | None


class StreakOut(BaseModel):
    days: int
    quote: str = "Consistency is the bridge between goals and accomplishment."


class WeightPoint(BaseModel):
    day: str
    weight_kg: float


class WeightHistoryOut(BaseModel):
    points: list[WeightPoint]
    current_kg: float | None
    trend_label: str | None


class ActivityMixRow(BaseModel):
    label: str
    hours: float


class ActivityMixOut(BaseModel):
    rows: list[ActivityMixRow]
    ring_pct: int


class TrendsInsightOut(BaseModel):
    text: str | None


@router.get("/profile", response_model=ProfileOut)
async def profile(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> ProfileOut:
    p = await _get_profile(db, user.id)
    return ProfileOut(
        email=user.email,
        display_name=p.display_name,
        bio=p.bio,
        level=p.level,
        membership_tier=p.membership_tier,
    )


@router.get("/goals", response_model=GoalsOut)
async def goals(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> GoalsOut:
    p = await _get_profile(db, user.id)
    steps_pct = min(1.0, p.steps_today / max(p.daily_steps_target, 1))
    weight_pct = 0.75
    progress = round(100 * (0.5 * steps_pct + 0.5 * weight_pct), 1)
    return GoalsOut(
        target_weight_kg=p.target_weight_kg,
        daily_steps_target=p.daily_steps_target,
        daily_protein_target_g=p.daily_protein_target_g,
        daily_calorie_target=p.daily_calorie_target,
        goal_progress_pct=progress,
    )


@router.get("/integrations", response_model=IntegrationsOut)
async def integrations(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> IntegrationsOut:
    p = await _get_profile(db, user.id)
    return IntegrationsOut(
        items=[
            IntegrationItem(
                id="apple_health",
                title="Apple Health",
                description="Sync vitals and activity",
                enabled=p.apple_health_enabled,
            ),
            IntegrationItem(
                id="google_fit",
                title="Google Fit",
                description="Connected since Oct 2023",
                enabled=p.google_fit_enabled,
            ),
        ]
    )


@router.get("/subscription", response_model=SubscriptionOut)
async def subscription(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> SubscriptionOut:
    p = await _get_profile(db, user.id)
    return SubscriptionOut(
        plan=p.subscription_plan,
        price_display=p.subscription_price_display,
        next_billing_date=p.next_billing_date,
    )


@router.post("/logout", status_code=204)
async def logout(response: Response) -> None:
    response.status_code = 204


@router.get("/dashboard", response_model=DashboardOut)
async def dashboard(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> DashboardOut:
    p = await _get_profile(db, user.id)
    res = await db.execute(
        select(BiometricSnapshot).where(BiometricSnapshot.user_id == user.id).order_by(BiometricSnapshot.recorded_at.desc())
    )
    snaps = res.scalars().all()
    biometrics = [
        {"metric": s.metric_key, "value": s.value, "change": s.change_label} for s in snaps[:8]
    ]
    return DashboardOut(
        active_energy_kcal=p.active_energy_kcal_today,
        steps=p.steps_today,
        sleep_minutes=p.sleep_minutes_today,
        insight=p.insight_body,
        hydration_target_ml=p.hydration_target_ml,
        hydration_current_ml=p.hydration_current_ml,
        next_workout_title=p.next_workout_title,
        biometrics=biometrics,
    )


@router.get("/momentum", response_model=MomentumOut)
async def momentum(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> MomentumOut:
    p = await _get_profile(db, user.id)
    return MomentumOut(
        status=p.momentum_status,
        bmi=p.bmi,
        weight_change_month_kg=p.weight_change_month_kg,
        regional_rank_label=p.regional_rank_label,
    )


@router.get("/streak", response_model=StreakOut)
async def streak(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> StreakOut:
    p = await _get_profile(db, user.id)
    return StreakOut(days=p.streak_days)


@router.get("/weight-history", response_model=WeightHistoryOut)
async def weight_history(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> WeightHistoryOut:
    res = await db.execute(
        select(WeightEntry).where(WeightEntry.user_id == user.id).order_by(WeightEntry.recorded_on.asc())
    )
    rows = res.scalars().all()
    points = [
        WeightPoint(day=r.recorded_on.strftime("%a").upper()[:3], weight_kg=r.weight_kg) for r in rows[-7:]
    ]
    current = rows[-1].weight_kg if rows else None
    return WeightHistoryOut(points=points, current_kg=current, trend_label="↓ 0.8kg since last Mon" if current else None)


@router.get("/activity-mix", response_model=ActivityMixOut)
async def activity_mix(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> ActivityMixOut:
    res = await db.execute(select(ActivityMixStat).where(ActivityMixStat.user_id == user.id))
    rows = res.scalars().all()
    if not rows:
        return ActivityMixOut(rows=[], ring_pct=0)
    total = sum(r.hours for r in rows) or 1.0
    strength = next((r.hours for r in rows if "Strength" in r.label), rows[0].hours)
    ring = int(min(100, round(100 * strength / total)))
    return ActivityMixOut(
        rows=[ActivityMixRow(label=r.label, hours=r.hours) for r in rows],
        ring_pct=ring,
    )


@router.get("/insights", response_model=TrendsInsightOut)
async def trends_insight(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> TrendsInsightOut:
    p = await _get_profile(db, user.id)
    return TrendsInsightOut(text=p.trends_insight or p.insight_body)


async def _get_profile(db: AsyncSession, user_id: UUID) -> UserProfile:
    res = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    p = res.scalar_one_or_none()
    if not p:
        p = UserProfile(user_id=user_id)
        db.add(p)
        await db.commit()
        await db.refresh(p)
    return p
