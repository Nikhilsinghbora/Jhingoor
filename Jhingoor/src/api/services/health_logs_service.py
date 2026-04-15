from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MenstrualCycle, MoodLog, NutritionLog, SleepLog


class HealthLogsService:
    async def upsert_nutrition_log(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        log_date: date,
        calories: int,
        protein: int,
        carbs: int,
        fat: int,
        source: str,
    ) -> NutritionLog:
        stmt = select(NutritionLog).where(NutritionLog.user_id == user_id, NutritionLog.date == log_date)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.calories = calories
            existing.protein = protein
            existing.carbs = carbs
            existing.fat = fat
            existing.source = source
            await db.commit()
            await db.refresh(existing)
            return existing

        row = NutritionLog(
            id=uuid4(),
            user_id=user_id,
            date=log_date,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat,
            source=source,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    async def upsert_sleep_log(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        log_date: date,
        sleep_hours: float,
        sleep_quality: int,
    ) -> SleepLog:
        stmt = select(SleepLog).where(SleepLog.user_id == user_id, SleepLog.date == log_date)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.sleep_hours = sleep_hours
            existing.sleep_quality = sleep_quality
            await db.commit()
            await db.refresh(existing)
            return existing

        row = SleepLog(
            id=uuid4(),
            user_id=user_id,
            date=log_date,
            sleep_hours=sleep_hours,
            sleep_quality=sleep_quality,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    async def upsert_mood_log(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        log_date: date,
        mood: str,
        energy_level: int,
        notes: str | None,
    ) -> MoodLog:
        stmt = select(MoodLog).where(MoodLog.user_id == user_id, MoodLog.date == log_date)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.mood = mood
            existing.energy_level = energy_level
            existing.notes = notes
            await db.commit()
            await db.refresh(existing)
            return existing

        row = MoodLog(
            id=uuid4(),
            user_id=user_id,
            date=log_date,
            mood=mood,
            energy_level=energy_level,
            notes=notes,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    async def upsert_cycle(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        period_start: date,
        period_end: date | None,
        cycle_length: int | None,
    ) -> MenstrualCycle:
        stmt = select(MenstrualCycle).where(
            MenstrualCycle.user_id == user_id, MenstrualCycle.period_start == period_start
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.period_end = period_end
            existing.cycle_length = cycle_length
            await db.commit()
            await db.refresh(existing)
            return existing

        row = MenstrualCycle(
            id=uuid4(),
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            cycle_length=cycle_length,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    async def get_recent_sleep_logs(self, db: AsyncSession, *, user_id: UUID, days: int = 7) -> list[SleepLog]:
        start_date = date.today() - timedelta(days=days)
        stmt = (
            select(SleepLog)
            .where(SleepLog.user_id == user_id, SleepLog.date >= start_date)
            .order_by(SleepLog.date.desc())
        )
        return list((await db.execute(stmt)).scalars().all())

    async def get_recent_mood_logs(self, db: AsyncSession, *, user_id: UUID, days: int = 14) -> list[MoodLog]:
        start_date = date.today() - timedelta(days=days)
        stmt = (
            select(MoodLog)
            .where(MoodLog.user_id == user_id, MoodLog.date >= start_date)
            .order_by(MoodLog.date.desc())
        )
        return list((await db.execute(stmt)).scalars().all())

    async def get_recent_nutrition_logs(
        self, db: AsyncSession, *, user_id: UUID, days: int = 7
    ) -> list[NutritionLog]:
        start_date = date.today() - timedelta(days=days)
        stmt = (
            select(NutritionLog)
            .where(NutritionLog.user_id == user_id, NutritionLog.date >= start_date)
            .order_by(NutritionLog.date.desc())
        )
        return list((await db.execute(stmt)).scalars().all())

    async def get_recent_cycles(self, db: AsyncSession, *, user_id: UUID, limit: int = 6) -> Sequence[MenstrualCycle]:
        stmt = (
            select(MenstrualCycle)
            .where(MenstrualCycle.user_id == user_id)
            .order_by(MenstrualCycle.period_start.desc())
            .limit(limit)
        )
        return list((await db.execute(stmt)).scalars().all())
