from __future__ import annotations

from datetime import datetime, timedelta, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.types import AgentResult
from database.models import MoodLog, NutritionLog, SleepLog, Workout


class BehaviorAgent:
    async def run(self, user_id: UUID, db: AsyncSession) -> AgentResult:
        start_datetime = datetime.now(UTC) - timedelta(days=7)
        start_day = start_datetime.date()
        workouts = (
            await db.execute(select(Workout).where(Workout.user_id == user_id, Workout.created_at >= start_datetime))
        ).scalars().all()
        sleep_logs = (
            await db.execute(select(SleepLog).where(SleepLog.user_id == user_id, SleepLog.date >= start_day))
        ).scalars().all()
        nutrition_logs = (
            await db.execute(select(NutritionLog).where(NutritionLog.user_id == user_id, NutritionLog.date >= start_day))
        ).scalars().all()
        mood_logs = (
            await db.execute(select(MoodLog).where(MoodLog.user_id == user_id, MoodLog.date >= start_day))
        ).scalars().all()

        consistency_days = len({*{w.created_at.date() for w in workouts}, *{s.date for s in sleep_logs}})
        missed_habits: list[str] = []
        if not workouts:
            missed_habits.append("workout")
        if not sleep_logs:
            missed_habits.append("sleep")
        if not nutrition_logs:
            missed_habits.append("nutrition")
        if not mood_logs:
            missed_habits.append("mood")

        return AgentResult(
            name="behavior",
            summary=f"Consistency tracked on {consistency_days} of last 7 days.",
            payload={"consistency_days": consistency_days, "missed_habits": missed_habits},
        )
