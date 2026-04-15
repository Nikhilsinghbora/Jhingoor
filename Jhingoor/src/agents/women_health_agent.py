from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.tools import infer_cycle_phase
from agents.types import AgentResult
from database.models import MenstrualCycle


class WomenHealthAgent:
    async def run(self, user_id: UUID, db: AsyncSession) -> AgentResult:
        latest_cycle = (
            await db.execute(
                select(MenstrualCycle).where(MenstrualCycle.user_id == user_id).order_by(MenstrualCycle.period_start.desc()).limit(1)
            )
        ).scalar_one_or_none()
        if not latest_cycle:
            return AgentResult(
                name="women_health",
                summary="No menstrual cycle data available yet.",
                payload={"phase": None, "cycle_length": None, "effective_cycle_length": 28},
            )

        effective_cycle_length = latest_cycle.cycle_length or 28
        phase = infer_cycle_phase(
            period_start=latest_cycle.period_start,
            cycle_length=effective_cycle_length,
            on_date=date.today(),
        )
        return AgentResult(
            name="women_health",
            summary=f"Current estimated cycle phase: {phase}.",
            payload={
                "phase": phase,
                "cycle_length": latest_cycle.cycle_length,
                "effective_cycle_length": effective_cycle_length,
            },
        )
