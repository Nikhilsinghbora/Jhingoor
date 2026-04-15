"""Add health intelligence log tables.

Revision ID: 20260414_0002
Revises: 20260413_0001
Create Date: 2026-04-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260414_0002"
down_revision: Union[str, None] = "20260413_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "nutrition_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("protein", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("carbs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fat", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="uq_nutrition_log_user_date"),
    )
    op.create_index(op.f("ix_nutrition_logs_date"), "nutrition_logs", ["date"], unique=False)
    op.create_index(op.f("ix_nutrition_logs_user_id"), "nutrition_logs", ["user_id"], unique=False)

    op.create_table(
        "sleep_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sleep_hours", sa.Float(), nullable=False, server_default="0"),
        sa.Column("sleep_quality", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="uq_sleep_log_user_date"),
    )
    op.create_index(op.f("ix_sleep_logs_date"), "sleep_logs", ["date"], unique=False)
    op.create_index(op.f("ix_sleep_logs_user_id"), "sleep_logs", ["user_id"], unique=False)

    op.create_table(
        "mood_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mood", sa.String(length=32), nullable=False),
        sa.Column("energy_level", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="uq_mood_log_user_date"),
    )
    op.create_index(op.f("ix_mood_logs_date"), "mood_logs", ["date"], unique=False)
    op.create_index(op.f("ix_mood_logs_user_id"), "mood_logs", ["user_id"], unique=False)

    op.create_table(
        "menstrual_cycles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("cycle_length", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_menstrual_cycles_period_start"), "menstrual_cycles", ["period_start"], unique=False)
    op.create_index(op.f("ix_menstrual_cycles_user_id"), "menstrual_cycles", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_menstrual_cycles_user_id"), table_name="menstrual_cycles")
    op.drop_index(op.f("ix_menstrual_cycles_period_start"), table_name="menstrual_cycles")
    op.drop_table("menstrual_cycles")

    op.drop_index(op.f("ix_mood_logs_user_id"), table_name="mood_logs")
    op.drop_index(op.f("ix_mood_logs_date"), table_name="mood_logs")
    op.drop_table("mood_logs")

    op.drop_index(op.f("ix_sleep_logs_user_id"), table_name="sleep_logs")
    op.drop_index(op.f("ix_sleep_logs_date"), table_name="sleep_logs")
    op.drop_table("sleep_logs")

    op.drop_index(op.f("ix_nutrition_logs_user_id"), table_name="nutrition_logs")
    op.drop_index(op.f("ix_nutrition_logs_date"), table_name="nutrition_logs")
    op.drop_table("nutrition_logs")
