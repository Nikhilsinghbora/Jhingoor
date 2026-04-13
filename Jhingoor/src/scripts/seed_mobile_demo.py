"""
Populate demo data for a mobile app user (run after migrations).

Usage (from repo root, with PYTHONPATH=src and .env loaded):
  uv run python -m scripts.seed_mobile_demo
"""

import asyncio
import os
import sys
import uuid
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import select

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from database.models import (  # noqa: E402
    ActivityMixStat,
    BiometricSnapshot,
    ChatMessage,
    HydrationDay,
    Meal,
    User,
    UserProfile,
    WeeklyIntensityPoint,
    WeightEntry,
    Workout,
)
from database.session import AsyncSessionLocal  # noqa: E402


DEMO_EMAIL = os.getenv("SEED_DEMO_EMAIL", "demo@jhingoor.app")
DEMO_PASSWORD = os.getenv("SEED_DEMO_PASSWORD", "DemoPass123!")


async def seed() -> uuid.UUID | None:
    async with AsyncSessionLocal() as session:
        existing = await session.execute(select(User).where(User.email == DEMO_EMAIL))
        if existing.scalar_one_or_none():
            print("Demo user already exists, skipping seed.")
            return None

        uid = uuid.uuid4()
        user = User(
            id=uid,
            email=DEMO_EMAIL,
            password_hash=pwd_context.hash(DEMO_PASSWORD),
        )
        session.add(user)
        profile = UserProfile(
            user_id=uid,
            display_name="Elena Volkov",
            bio="Elite performance athlete focusing on metabolic efficiency and explosive strength.",
            level=42,
            membership_tier="premium",
            target_weight_kg=64.5,
            daily_steps_target=12000,
            daily_protein_target_g=120,
            daily_calorie_target=2200,
            apple_health_enabled=True,
            google_fit_enabled=False,
            subscription_plan="Elite Coaching",
            subscription_price_display="$14.99/mo",
            next_billing_date=date(2026, 11, 12),
            active_energy_kcal_today=1842,
            steps_today=12402,
            sleep_minutes_today=440,
            insight_body=(
                "Your aerobic capacity increased by 4% this week. "
                "Pushing today's HIIT by 5 minutes will trigger peak metabolic adaptation."
            ),
            trends_insight=(
                "Your weight drop correlates with the increased intensity in Thursday's leg sessions. "
                "Maintaining current caloric intake will stabilize lean mass growth."
            ),
            momentum_status="Excellent",
            streak_days=7,
            bmi=24.5,
            weight_change_month_kg=-2.4,
            regional_rank_label="TOP 5% IN REGION",
            hydration_target_ml=3500,
            hydration_current_ml=1200,
            next_workout_title="Lower Body Power",
        )
        session.add(profile)

        now = datetime.now(timezone.utc)
        session.add(
            Workout(
                user_id=uid,
                workout_type="HIIT",
                duration_min=45,
                intensity=8,
                calories=420,
                avg_hr=152,
                sets_count=12,
                status="completed",
                title="High Intensity Interval Training",
                subtitle="Morning Session • 45 mins • 420 kcal",
                starts_at=now.replace(hour=8, minute=0, second=0, microsecond=0),
            )
        )
        session.add(
            Meal(
                user_id=uid,
                name="Greek Yogurt Bowl with Berries",
                calories=320,
                protein_g=24,
                carbs_g=35,
                fats_g=8,
                logged_at=now.replace(hour=9, minute=15, second=0, microsecond=0),
            )
        )
        session.add(
            Workout(
                user_id=uid,
                workout_type="scheduled",
                duration_min=0,
                intensity=0,
                calories=0,
                status="scheduled",
                title="Afternoon Hydration & Snack",
                subtitle="Wait for the pulse...",
                starts_at=now.replace(hour=13, minute=0, second=0, microsecond=0),
            )
        )

        session.add(
            ChatMessage(
                user_id=uid,
                role="user",
                content=(
                    "I'm feeling a bit sluggish today. Should I push through my heavy squats "
                    "or swap for active recovery?"
                ),
            )
        )
        session.add(
            ChatMessage(
                user_id=uid,
                role="assistant",
                content=(
                    "Based on your heart rate variability and sleep debt, "
                    "active recovery today will preserve strength gains for tomorrow's session."
                ),
            )
        )

        today = date.today()
        session.add(HydrationDay(user_id=uid, log_date=today, total_ml=1200))

        for i in range(7):
            d = today - timedelta(days=6 - i)
            session.add(
                WeightEntry(
                    user_id=uid,
                    weight_kg=82.4 + (i - 3) * 0.1,
                    recorded_on=d,
                )
            )

        week_start = today - timedelta(days=today.weekday())
        for day_i, val in enumerate([0.3, 0.5, 0.9, 0.4, 0.6, 0.55, 0.5]):
            session.add(
                WeeklyIntensityPoint(
                    user_id=uid,
                    day_index=day_i,
                    value=val,
                    week_start=week_start,
                )
            )

        session.add(
            ActivityMixStat(
                user_id=uid,
                label="Strength Training",
                hours=12.0,
                period_start=week_start,
                period_end=week_start + timedelta(days=6),
            )
        )
        session.add(
            ActivityMixStat(
                user_id=uid,
                label="Cardio Sessions",
                hours=4.0,
                period_start=week_start,
                period_end=week_start + timedelta(days=6),
            )
        )

        for key, val, ch in [
            ("rhr", 58.0, "-2%"),
            ("weight", 76.4, "-0.8"),
            ("vo2", 52.1, "+1.4"),
            ("recovery", 88.0, "Optimal"),
        ]:
            session.add(
                BiometricSnapshot(
                    user_id=uid,
                    metric_key=key,
                    value=val,
                    change_label=ch,
                )
            )

        await session.commit()
        print(f"Seeded demo user {DEMO_EMAIL} id={uid}")
        return uid


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
