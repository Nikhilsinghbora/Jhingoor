from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.types import AgentResult
from database.models import SleepLog, UserProfile, Workout


class WorkoutAgent:
    async def run(self, user_id: UUID, db: AsyncSession) -> AgentResult:
        profile = (await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))).scalar_one_or_none()
        latest_sleep = (
            await db.execute(select(SleepLog).where(SleepLog.user_id == user_id).order_by(SleepLog.date.desc()).limit(1))
        ).scalar_one_or_none()

        intensity = 7
        if latest_sleep and latest_sleep.sleep_hours < 6:
            intensity = 5
        if latest_sleep and latest_sleep.sleep_hours < 5:
            intensity = 4

        suggestion = {
            "title": "Strength + Mobility",
            "duration_min": 45 if intensity >= 6 else 30,
            "intensity": intensity,
            "focus": "full body",
        }
        next_workout_title = profile.next_workout_title if profile else None
        recent_workouts = (
            await db.execute(select(Workout).where(Workout.user_id == user_id).order_by(Workout.created_at.desc()).limit(5))
        ).scalars().all()

        return AgentResult(
            name="workout",
            summary=f"Suggested workout intensity {intensity}/10.",
            payload={
                "suggestion": suggestion,
                "next_workout_title": next_workout_title,
                "recent_workouts_count": len(recent_workouts),
            },
        )
