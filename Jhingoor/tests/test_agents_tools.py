from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from agents.orchestrator_agent import OrchestratorAgent
from agents.tools.calorie_calculator import calculate_bmr, calculate_tdee
from agents.tools.cycle_phase import infer_cycle_phase
from agents.tools.food_search import search_foods
from agents.tools.macro_calculator import calculate_macros
from agents.tools.sleep_score import calculate_sleep_score


def test_calorie_and_macro_calculators() -> None:
    bmr = calculate_bmr(weight_kg=70, height_cm=175, age=30, sex="male")
    tdee = calculate_tdee(bmr=bmr, activity_multiplier=1.5)
    macros = calculate_macros(tdee)
    assert bmr > 1000
    assert tdee > bmr
    assert macros["protein_g"] > 0


def test_sleep_score_and_cycle_phase() -> None:
    score = calculate_sleep_score(hours=7.5, quality=8)
    phase = infer_cycle_phase(period_start=date.today(), cycle_length=28)
    assert score > 0
    assert phase in {"menstrual", "follicular", "ovulation", "luteal"}


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"weight_kg": 0, "height_cm": 175, "age": 30, "sex": "male"}, "weight_kg"),
        ({"weight_kg": 70, "height_cm": 0, "age": 30, "sex": "male"}, "height_cm"),
        ({"weight_kg": 70, "height_cm": 175, "age": 0, "sex": "male"}, "age"),
        ({"weight_kg": 70, "height_cm": 175, "age": 30, "sex": "other"}, "sex"),
    ],
)
def test_calculate_bmr_rejects_invalid_input(kwargs: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        calculate_bmr(**kwargs)


def test_calculate_tdee_rejects_invalid_multiplier() -> None:
    with pytest.raises(ValueError, match="activity_multiplier"):
        calculate_tdee(1600, activity_multiplier=0.8)


def test_calculate_macros_rejects_invalid_ratios() -> None:
    with pytest.raises(ValueError, match="less than or equal"):
        calculate_macros(2200, protein_ratio=0.6, carb_ratio=0.5)


def test_calculate_sleep_score_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="hours"):
        calculate_sleep_score(hours=26, quality=8)
    with pytest.raises(ValueError, match="quality"):
        calculate_sleep_score(hours=7.5, quality=0)


def test_infer_cycle_phase_boundaries() -> None:
    start = date(2026, 1, 1)
    assert infer_cycle_phase(period_start=start, cycle_length=28, on_date=start) == "menstrual"
    assert infer_cycle_phase(period_start=start, cycle_length=28, on_date=date(2026, 1, 6)) == "follicular"
    assert infer_cycle_phase(period_start=start, cycle_length=28, on_date=date(2026, 1, 14)) == "ovulation"
    assert infer_cycle_phase(period_start=start, cycle_length=28, on_date=date(2026, 1, 18)) == "luteal"


def test_infer_cycle_phase_rejects_invalid_cycle_length() -> None:
    with pytest.raises(ValueError, match="cycle_length"):
        infer_cycle_phase(period_start=date(2026, 1, 1), cycle_length=0)


@pytest.mark.asyncio
async def test_search_foods_rejects_invalid_limit() -> None:
    with pytest.raises(ValueError, match="limit"):
        await search_foods("eggs", limit=0)


@pytest.mark.asyncio
async def test_search_foods_fallback_on_provider_failure() -> None:
    service = SimpleNamespace(search=AsyncMock(side_effect=RuntimeError("boom")))
    result = await search_foods("eggs", service=service, limit=3)
    assert result == []


def test_orchestrator_summary_builder() -> None:
    orchestrator = OrchestratorAgent()
    text = orchestrator._build_human_summary({"diet": {"summary": "x"}, "recovery": {"summary": "y"}})
    assert "diet" in text
    assert "recovery" in text


@pytest.mark.asyncio
async def test_orchestrator_ai_fallback_and_agent_isolation() -> None:
    orchestrator = OrchestratorAgent()
    user_id = uuid4()
    db = object()

    orchestrator.diet_agent.run = AsyncMock(return_value=SimpleNamespace(summary="diet ok", payload={"a": 1}))
    orchestrator.workout_agent.run = AsyncMock(side_effect=RuntimeError("db failed"))
    orchestrator.recovery_agent.run = AsyncMock(return_value=SimpleNamespace(summary="recovery ok", payload={"b": 2}))
    orchestrator.behavior_agent.run = AsyncMock(return_value=SimpleNamespace(summary="behavior ok", payload={"c": 3}))
    orchestrator.women_health_agent.run = AsyncMock(return_value=SimpleNamespace(summary="women ok", payload={"d": 4}))
    orchestrator._optional_ai_enhancement = AsyncMock(return_value="fallback summary")

    result = await orchestrator.run(user_id=user_id, db=db)
    assert result["summary"] == "fallback summary"
    assert "structured" in result
    assert result["structured"]["diet"]["summary"] == "diet ok"
    assert result["structured"]["workout"]["payload"]["status"] == "unavailable"
    assert result["structured"]["errors"]["workout"] == "agent_execution_failed"
