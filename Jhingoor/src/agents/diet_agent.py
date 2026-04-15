from __future__ import annotations

from dataclasses import asdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.tools import calculate_bmr, calculate_macros, calculate_tdee, search_foods
from agents.types import AgentResult
from database.models import UserProfile


class DietAgent:
    async def run(self, user_id: UUID, db: AsyncSession) -> AgentResult:
        profile = (await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))).scalar_one_or_none()

        weight_kg = profile.target_weight_kg if profile and profile.target_weight_kg else 70.0
        height_cm = 170.0
        age = 30
        sex = "male"
        bmr = calculate_bmr(weight_kg=weight_kg, height_cm=height_cm, age=age, sex=sex)
        tdee = calculate_tdee(bmr, activity_multiplier=1.45)
        macros = calculate_macros(tdee)
        foods = await search_foods("high protein breakfast", limit=3)

        return AgentResult(
            name="diet",
            summary=f"Daily target {macros['calories']} kcal with {macros['protein_g']}g protein.",
            payload={
                "bmr": round(bmr, 2),
                "tdee": tdee,
                "macros": macros,
                "meal_suggestions": [asdict(item) for item in foods],
                "assumptions": {
                    "weight_kg": weight_kg,
                    "height_cm": height_cm,
                    "age": age,
                    "sex": sex,
                },
            },
        )
