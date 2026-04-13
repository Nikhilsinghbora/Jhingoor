"""Mobile app schema: app_users, workouts, meals, chat, trends helpers.

Revision ID: 20260413_0001
Revises:
Create Date: 2026-04-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260413_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_app_users_email"), "app_users", ["email"], unique=True)

    op.create_table(
        "oauth_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_user_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_sub"),
    )
    op.create_index(op.f("ix_oauth_accounts_provider"), "oauth_accounts", ["provider"], unique=False)

    op.create_table(
        "user_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False, server_default="Athlete"),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("membership_tier", sa.String(length=64), nullable=False, server_default="free"),
        sa.Column("target_weight_kg", sa.Float(), nullable=True),
        sa.Column("daily_steps_target", sa.Integer(), nullable=False, server_default="12000"),
        sa.Column("daily_protein_target_g", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("daily_calorie_target", sa.Integer(), nullable=False, server_default="2200"),
        sa.Column("apple_health_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("google_fit_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("subscription_plan", sa.String(length=120), nullable=True),
        sa.Column("subscription_price_display", sa.String(length=32), nullable=True),
        sa.Column("next_billing_date", sa.Date(), nullable=True),
        sa.Column("active_energy_kcal_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("steps_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sleep_minutes_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("insight_body", sa.Text(), nullable=True),
        sa.Column("trends_insight", sa.Text(), nullable=True),
        sa.Column("momentum_status", sa.String(length=64), nullable=True),
        sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bmi", sa.Float(), nullable=True),
        sa.Column("weight_change_month_kg", sa.Float(), nullable=True),
        sa.Column("regional_rank_label", sa.String(length=64), nullable=True),
        sa.Column("hydration_target_ml", sa.Integer(), nullable=False, server_default="3500"),
        sa.Column("hydration_current_ml", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_workout_title", sa.String(length=200), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "workouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workout_type", sa.String(length=120), nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("intensity", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("calories", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_hr", sa.Integer(), nullable=True),
        sa.Column("sets_count", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="completed"),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("subtitle", sa.String(length=300), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "meals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("protein_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("carbs_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fats_g", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "weight_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("recorded_on", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_weight_entries_recorded_on"), "weight_entries", ["recorded_on"], unique=False)

    op.create_table(
        "hydration_days",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("log_date", sa.Date(), nullable=False),
        sa.Column("total_ml", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "log_date"),
    )

    op.create_table(
        "activity_mix_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("hours", sa.Float(), nullable=False, server_default="0"),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "label", "period_start", "period_end", name="uq_mix_period"),
    )

    op.create_table(
        "weekly_intensity_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("day_index", sa.Integer(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "day_index", "week_start", name="uq_intensity_week_day"),
    )

    op.create_table(
        "biometric_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_key", sa.String(length=32), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("change_label", sa.String(length=32), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("biometric_snapshots")
    op.drop_table("weekly_intensity_points")
    op.drop_table("activity_mix_stats")
    op.drop_table("hydration_days")
    op.drop_index(op.f("ix_weight_entries_recorded_on"), table_name="weight_entries")
    op.drop_table("weight_entries")
    op.drop_table("chat_messages")
    op.drop_table("meals")
    op.drop_table("workouts")
    op.drop_table("user_profiles")
    op.drop_index(op.f("ix_oauth_accounts_provider"), table_name="oauth_accounts")
    op.drop_table("oauth_accounts")
    op.drop_index(op.f("ix_app_users_email"), table_name="app_users")
    op.drop_table("app_users")
