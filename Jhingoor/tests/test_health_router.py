from __future__ import annotations

from datetime import UTC, date, datetime
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from api.deps import get_current_user, get_db
from api.main import app
from api.routers import health


async def _override_db():
    yield None


async def _override_user():
    return SimpleNamespace(id=uuid4())


def _client() -> TestClient:
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_user
    return TestClient(app)


def test_nutrition_log_endpoint() -> None:
    client = _client()

    async def _upsert(*args, **kwargs):
        return SimpleNamespace(
            id=uuid4(),
            date=kwargs["log_date"],
            calories=kwargs["calories"],
            protein=kwargs["protein"],
            carbs=kwargs["carbs"],
            fat=kwargs["fat"],
            source=kwargs["source"],
            created_at=datetime.now(UTC),
        )

    health.health_logs_service.upsert_nutrition_log = _upsert
    payload = {"date": "2026-04-14", "calories": 2100, "protein": 140, "carbs": 230, "fat": 65, "source": "manual"}
    res = client.post("/api/v1/health/nutrition/log", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["calories"] == 2100
    assert body["source"] == "manual"


def test_recovery_endpoint() -> None:
    client = _client()

    async def _run(*args, **kwargs):
        return SimpleNamespace(payload={"score": 82.0, "status": "good", "sleep_entries": 6})

    health.recovery_agent.run = _run
    res = client.get("/api/v1/health/recovery")
    assert res.status_code == 200
    assert res.json() == {"score": 82.0, "status": "good", "sleep_entries": 6}


def test_recovery_endpoint_defaults_when_payload_missing() -> None:
    client = _client()

    async def _run(*args, **kwargs):
        return SimpleNamespace(payload={})

    health.recovery_agent.run = _run
    res = client.get("/api/v1/health/recovery")
    assert res.status_code == 200
    assert res.json() == {"score": 0.0, "status": "unknown", "sleep_entries": 0}


def test_nutrition_plan_endpoint_contract() -> None:
    client = _client()

    async def _run(*args, **kwargs):
        return SimpleNamespace(
            summary="Daily target",
            payload={
                "tdee": 2140.5,
                "macros": {"calories": 2140, "protein_g": 160, "carbs_g": 200, "fat_g": 70},
                "meal_suggestions": [{"name": "Greek Yogurt Bowl"}],
            },
        )

    health.diet_agent.run = _run
    res = client.get("/api/v1/health/nutrition/plan")
    assert res.status_code == 200
    assert res.json()["summary"] == "Daily target"
    assert res.json()["tdee"] == 2140.5
    assert isinstance(res.json()["meals"], list)


def test_nutrition_plan_endpoint_defaults_when_payload_missing() -> None:
    client = _client()

    async def _run(*args, **kwargs):
        return SimpleNamespace(summary="No data", payload={})

    health.diet_agent.run = _run
    res = client.get("/api/v1/health/nutrition/plan")
    assert res.status_code == 200
    assert res.json() == {"summary": "No data", "tdee": 0.0, "macros": {}, "meals": []}


def test_sleep_log_endpoint() -> None:
    client = _client()

    async def _upsert(*args, **kwargs):
        return SimpleNamespace(
            id=uuid4(),
            date=kwargs["log_date"],
            sleep_hours=kwargs["sleep_hours"],
            sleep_quality=kwargs["sleep_quality"],
        )

    health.health_logs_service.upsert_sleep_log = _upsert
    payload = {"date": "2026-04-14", "sleep_hours": 7.5, "sleep_quality": 8}
    res = client.post("/api/v1/health/sleep/log", json=payload)
    assert res.status_code == 200
    assert res.json()["sleep_hours"] == 7.5
    assert res.json()["sleep_quality"] == 8


def test_mood_log_endpoint() -> None:
    client = _client()

    async def _upsert(*args, **kwargs):
        return SimpleNamespace(
            id=uuid4(),
            date=kwargs["log_date"],
            mood=kwargs["mood"],
            energy_level=kwargs["energy_level"],
            notes=kwargs["notes"],
        )

    health.health_logs_service.upsert_mood_log = _upsert
    payload = {"date": "2026-04-14", "mood": "great", "energy_level": 8, "notes": "Solid day"}
    res = client.post("/api/v1/health/mood/log", json=payload)
    assert res.status_code == 200
    assert res.json()["mood"] == "great"
    assert res.json()["energy_level"] == 8


def test_advanced_insights_endpoint_contract() -> None:
    client = _client()

    async def _run(*args, **kwargs):
        return {
            "summary": "Actionable insights",
            "structured": {"diet": {"summary": "ok", "payload": {}}, "errors": {}},
        }

    health.orchestrator_agent.run = _run
    res = client.get("/api/v1/health/insights/advanced")
    assert res.status_code == 200
    body = res.json()
    assert set(body.keys()) == {"summary", "structured"}
    assert body["summary"] == "Actionable insights"


def test_mood_log_validation_error() -> None:
    client = _client()
    payload = {"date": str(date.today()), "mood": "ok", "energy_level": 11}
    res = client.post("/api/v1/health/mood/log", json=payload)
    assert res.status_code == 422
