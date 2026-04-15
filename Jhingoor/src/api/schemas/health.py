from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class NutritionLogIn(BaseModel):
    date: date
    calories: int = Field(ge=0, le=20000)
    protein: int = Field(ge=0, le=1000)
    carbs: int = Field(ge=0, le=2000)
    fat: int = Field(ge=0, le=1000)
    source: str = Field(default="manual", max_length=32)


class NutritionLogOut(BaseModel):
    id: str
    date: date
    calories: int
    protein: int
    carbs: int
    fat: int
    source: str
    created_at: datetime


class NutritionPlanOut(BaseModel):
    summary: str
    tdee: float
    macros: dict[str, int]
    meals: list[dict]


class SleepLogIn(BaseModel):
    date: date
    sleep_hours: float = Field(gt=0, le=24)
    sleep_quality: int = Field(ge=1, le=10)


class SleepLogOut(BaseModel):
    id: str
    date: date
    sleep_hours: float
    sleep_quality: int


class MoodLogIn(BaseModel):
    date: date
    mood: str = Field(min_length=2, max_length=32)
    energy_level: int = Field(ge=1, le=10)
    notes: str | None = Field(default=None, max_length=2000)


class MoodLogOut(BaseModel):
    id: str
    date: date
    mood: str
    energy_level: int
    notes: str | None


class RecoveryOut(BaseModel):
    score: float
    status: str
    sleep_entries: int


class AdvancedInsightsOut(BaseModel):
    summary: str
    structured: dict
