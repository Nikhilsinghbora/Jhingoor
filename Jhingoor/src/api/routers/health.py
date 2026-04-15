from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from agents.diet_agent import DietAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.recovery_agent import RecoveryAgent
from api.deps import CurrentUser, get_db
from api.schemas.health import (
    AdvancedInsightsOut,
    MoodLogIn,
    MoodLogOut,
    NutritionLogIn,
    NutritionLogOut,
    NutritionPlanOut,
    RecoveryOut,
    SleepLogIn,
    SleepLogOut,
)
from api.services.health_logs_service import HealthLogsService

router = APIRouter(prefix="/health", tags=["health"])

health_logs_service = HealthLogsService()
diet_agent = DietAgent()
recovery_agent = RecoveryAgent()
orchestrator_agent = OrchestratorAgent()


@router.post("/nutrition/log", response_model=NutritionLogOut)
async def nutrition_log(
    payload: NutritionLogIn, user: CurrentUser, db: AsyncSession = Depends(get_db)
) -> NutritionLogOut:
    row = await health_logs_service.upsert_nutrition_log(
        db,
        user_id=user.id,
        log_date=payload.date,
        calories=payload.calories,
        protein=payload.protein,
        carbs=payload.carbs,
        fat=payload.fat,
        source=payload.source,
    )
    return NutritionLogOut(
        id=str(row.id),
        date=row.date,
        calories=row.calories,
        protein=row.protein,
        carbs=row.carbs,
        fat=row.fat,
        source=row.source,
        created_at=row.created_at,
    )


@router.get("/nutrition/plan", response_model=NutritionPlanOut)
async def nutrition_plan(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> NutritionPlanOut:
    result = await diet_agent.run(user.id, db)
    payload = result.payload
    return NutritionPlanOut(
        summary=result.summary,
        tdee=float(payload.get("tdee", 0.0)),
        macros=payload.get("macros", {}),
        meals=payload.get("meal_suggestions", []),
    )


@router.post("/sleep/log", response_model=SleepLogOut)
async def sleep_log(payload: SleepLogIn, user: CurrentUser, db: AsyncSession = Depends(get_db)) -> SleepLogOut:
    row = await health_logs_service.upsert_sleep_log(
        db,
        user_id=user.id,
        log_date=payload.date,
        sleep_hours=payload.sleep_hours,
        sleep_quality=payload.sleep_quality,
    )
    return SleepLogOut(
        id=str(row.id),
        date=row.date,
        sleep_hours=row.sleep_hours,
        sleep_quality=row.sleep_quality,
    )


@router.get("/recovery", response_model=RecoveryOut)
async def recovery(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> RecoveryOut:
    result = await recovery_agent.run(user.id, db)
    return RecoveryOut(
        score=float(result.payload.get("score", 0.0)),
        status=str(result.payload.get("status", "unknown")),
        sleep_entries=int(result.payload.get("sleep_entries", 0)),
    )


@router.post("/mood/log", response_model=MoodLogOut)
async def mood_log(payload: MoodLogIn, user: CurrentUser, db: AsyncSession = Depends(get_db)) -> MoodLogOut:
    row = await health_logs_service.upsert_mood_log(
        db,
        user_id=user.id,
        log_date=payload.date,
        mood=payload.mood,
        energy_level=payload.energy_level,
        notes=payload.notes,
    )
    return MoodLogOut(
        id=str(row.id),
        date=row.date,
        mood=row.mood,
        energy_level=row.energy_level,
        notes=row.notes,
    )


@router.get("/insights/advanced", response_model=AdvancedInsightsOut)
async def advanced_insights(user: CurrentUser, db: AsyncSession = Depends(get_db)) -> AdvancedInsightsOut:
    result = await orchestrator_agent.run(user.id, db)
    return AdvancedInsightsOut(summary=result["summary"], structured=result["structured"])
