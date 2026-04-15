from __future__ import annotations

import json
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from agents.behavior_agent import BehaviorAgent
from agents.diet_agent import DietAgent
from agents.recovery_agent import RecoveryAgent
from agents.women_health_agent import WomenHealthAgent
from agents.workout_agent import WorkoutAgent


class OrchestratorAgent:
    def __init__(self) -> None:
        self.diet_agent = DietAgent()
        self.workout_agent = WorkoutAgent()
        self.recovery_agent = RecoveryAgent()
        self.behavior_agent = BehaviorAgent()
        self.women_health_agent = WomenHealthAgent()

    async def run(self, user_id: UUID, db: AsyncSession) -> dict:
        errors: dict[str, str] = {}
        agents = {
            "diet": await self._run_agent("diet", self.diet_agent.run, user_id, db, errors),
            "workout": await self._run_agent("workout", self.workout_agent.run, user_id, db, errors),
            "recovery": await self._run_agent("recovery", self.recovery_agent.run, user_id, db, errors),
            "behavior": await self._run_agent("behavior", self.behavior_agent.run, user_id, db, errors),
            "women_health": await self._run_agent("women_health", self.women_health_agent.run, user_id, db, errors),
        }
        readable = self._build_human_summary(agents)
        ai_text = await self._optional_ai_enhancement(agents, readable)
        if errors:
            agents["errors"] = errors
        return {"summary": ai_text, "structured": agents}

    @staticmethod
    def _build_human_summary(agents: dict) -> str:
        lines = [f"{name}: {entry['summary']}" for name, entry in agents.items()]
        return " | ".join(lines)

    async def _run_agent(self, name: str, runner, user_id: UUID, db: AsyncSession, errors: dict[str, str]) -> dict:
        try:
            result = await runner(user_id, db)
            return {"summary": result.summary, "payload": result.payload}
        except Exception as exc:
            logging.exception("Agent '%s' failed in orchestrator: %s", name, exc)
            errors[name] = "agent_execution_failed"
            return {"summary": f"{name} insights unavailable right now.", "payload": {"status": "unavailable"}}

    async def _optional_ai_enhancement(self, agents: dict, fallback: str) -> str:
        try:
            from bot.brain import process_multimodel

            prompt = (
                "You are a fitness intelligence orchestrator. "
                "Convert this JSON into concise, actionable insights with priorities. JSON:\n"
                f"{json.dumps(agents, default=str)}"
            )
            return await process_multimodel(prompt=prompt)
        except ImportError as exc:
            logging.warning("LLM enhancement unavailable due to import error: %s", exc)
            return fallback
        except RuntimeError as exc:
            logging.warning("LLM enhancement runtime error: %s", exc)
            return fallback
        except Exception as exc:
            logging.exception("Unexpected LLM enhancement failure: %s", exc)
            return fallback
