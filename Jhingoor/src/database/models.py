import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


# --- Legacy Telegram / existing tables (unchanged column names) ---


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    daily_goal_kcal: Mapped[int] = mapped_column(Integer, default=2000)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("profiles.id"))
    type: Mapped[str] = mapped_column(String)
    raw_text: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class DailyLog(Base):
    __tablename__ = "daily_logs"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("profiles.id"), primary_key=True)
    log_date: Mapped[date] = mapped_column(Date, primary_key=True, server_default=func.current_date())
    total_calories: Mapped[int] = mapped_column(Integer, default=0)
    total_protein: Mapped[int] = mapped_column(Integer, default=0)
    water_intake_ml: Mapped[int] = mapped_column(Integer, default=0)


# --- Mobile API domain ---


class OAuthProvider(str, enum.Enum):
    google = "google"
    apple = "apple"


class User(Base):
    __tablename__ = "app_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    profile: Mapped["UserProfile | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    workouts: Mapped[list["Workout"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    meals: Mapped[list["Meal"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    weight_entries: Mapped[list["WeightEntry"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    hydration_days: Mapped[list["HydrationDay"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    nutrition_logs: Mapped[list["NutritionLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sleep_logs: Mapped[list["SleepLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    mood_logs: Mapped[list["MoodLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    menstrual_cycles: Mapped[list["MenstrualCycle"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"
    __table_args__ = (UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_sub"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(32), index=True)
    provider_user_id: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), primary_key=True
    )
    display_name: Mapped[str] = mapped_column(String(200), default="Athlete")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    membership_tier: Mapped[str] = mapped_column(String(64), default="free")
    target_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    daily_steps_target: Mapped[int] = mapped_column(Integer, default=12000)
    daily_protein_target_g: Mapped[int] = mapped_column(Integer, default=120)
    daily_calorie_target: Mapped[int] = mapped_column(Integer, default=2200)
    apple_health_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    google_fit_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_plan: Mapped[str | None] = mapped_column(String(120), nullable=True)
    subscription_price_display: Mapped[str | None] = mapped_column(String(32), nullable=True)
    next_billing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    active_energy_kcal_today: Mapped[int] = mapped_column(Integer, default=0)
    steps_today: Mapped[int] = mapped_column(Integer, default=0)
    sleep_minutes_today: Mapped[int] = mapped_column(Integer, default=0)
    insight_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    trends_insight: Mapped[str | None] = mapped_column(Text, nullable=True)
    momentum_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    bmi: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_change_month_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    regional_rank_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hydration_target_ml: Mapped[int] = mapped_column(Integer, default=3500)
    hydration_current_ml: Mapped[int] = mapped_column(Integer, default=0)
    next_workout_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="profile")


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"))
    workout_type: Mapped[str] = mapped_column(String(120))
    duration_min: Mapped[int] = mapped_column(Integer, default=0)
    intensity: Mapped[int] = mapped_column(Integer, default=5)
    calories: Mapped[int] = mapped_column(Integer, default=0)
    avg_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sets_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    subtitle: Mapped[str | None] = mapped_column(String(300), nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="workouts")


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    calories: Mapped[int] = mapped_column(Integer, default=0)
    protein_g: Mapped[int] = mapped_column(Integer, default=0)
    carbs_g: Mapped[int] = mapped_column(Integer, default=0)
    fats_g: Mapped[int] = mapped_column(Integer, default=0)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="meals")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="chat_messages")


class WeightEntry(Base):
    __tablename__ = "weight_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"))
    weight_kg: Mapped[float] = mapped_column(Float)
    recorded_on: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="weight_entries")


class HydrationDay(Base):
    __tablename__ = "hydration_days"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), primary_key=True
    )
    log_date: Mapped[date] = mapped_column(Date, primary_key=True)
    total_ml: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="hydration_days")


class ActivityMixStat(Base):
    __tablename__ = "activity_mix_stats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(120))
    hours: Mapped[float] = mapped_column(Float, default=0.0)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)

    __table_args__ = (UniqueConstraint("user_id", "label", "period_start", "period_end", name="uq_mix_period"),)


class WeeklyIntensityPoint(Base):
    __tablename__ = "weekly_intensity_points"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"))
    day_index: Mapped[int] = mapped_column(Integer)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    week_start: Mapped[date] = mapped_column(Date)

    __table_args__ = (UniqueConstraint("user_id", "day_index", "week_start", name="uq_intensity_week_day"),)


class BiometricSnapshot(Base):
    __tablename__ = "biometric_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"))
    metric_key: Mapped[str] = mapped_column(String(32))
    value: Mapped[float] = mapped_column(Float)
    change_label: Mapped[str | None] = mapped_column(String(32), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NutritionLog(Base):
    __tablename__ = "nutrition_logs"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_nutrition_log_user_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, index=True)
    calories: Mapped[int] = mapped_column(Integer, default=0)
    protein: Mapped[int] = mapped_column(Integer, default=0)
    carbs: Mapped[int] = mapped_column(Integer, default=0)
    fat: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(32), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="nutrition_logs")


class SleepLog(Base):
    __tablename__ = "sleep_logs"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_sleep_log_user_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), index=True
    )
    sleep_hours: Mapped[float] = mapped_column(Float, default=0.0)
    sleep_quality: Mapped[int] = mapped_column(Integer, default=5)
    date: Mapped[date] = mapped_column(Date, index=True)

    user: Mapped["User"] = relationship(back_populates="sleep_logs")


class MoodLog(Base):
    __tablename__ = "mood_logs"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_mood_log_user_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), index=True
    )
    mood: Mapped[str] = mapped_column(String(32))
    energy_level: Mapped[int] = mapped_column(Integer, default=5)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, index=True)

    user: Mapped["User"] = relationship(back_populates="mood_logs")


class MenstrualCycle(Base):
    __tablename__ = "menstrual_cycles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), index=True
    )
    period_start: Mapped[date] = mapped_column(Date, index=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    cycle_length: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="menstrual_cycles")
