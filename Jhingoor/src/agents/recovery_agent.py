from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.tools import calculate_sleep_score
from agents.types import AgentResult
from database.models import SleepLog


class RecoveryAgent:
    async def run(self, user_id: UUID, db: AsyncSession) -> AgentResult:
        logs = (
            await db.execute(select(SleepLog).where(SleepLog.user_id == user_id).order_by(SleepLog.date.desc()).limit(7))
        ).scalars().all()
        if not logs:
            return AgentResult(
                name="recovery",
                summary="No sleep logs available yet.",
                payload={"score": 0.0, "status": "no_data", "sleep_entries": 0},
            )

        scores = [calculate_sleep_score(item.sleep_hours, item.sleep_quality) for item in logs]
        avg_score = round(sum(scores) / len(scores), 2)
        status = "good" if avg_score >= 75 else "moderate" if avg_score >= 55 else "low"
        return AgentResult(
            name="recovery",
            summary=f"Recovery score is {avg_score} ({status}).",
            payload={"score": avg_score, "status": status, "sleep_entries": len(logs)},
        )
