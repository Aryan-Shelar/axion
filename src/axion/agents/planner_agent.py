"""Planner Agent for creating structured execution plans."""

from __future__ import annotations

from dataclasses import dataclass
import re

from axion.ai.ai_core import AICore
from axion.ai.ollama_client import DEFAULT_MODEL


PLANNER_PROMPT = (
    "Create a practical execution plan for this goal. Return exactly 5 to 8 "
    "numbered steps. Each step should be short, clear, and actionable. Do not "
    "claim you executed anything."
)

FALLBACK_STEPS = [
    "Clarify the goal",
    "Break the goal into smaller tasks",
    "Gather required resources",
    "Start with the first small task",
    "Review progress and improve",
]


@dataclass(frozen=True)
class PlanDraft:
    """A plan draft before it is saved."""

    summary: str
    steps: list[dict]
    fallback_used: bool = False


class PlannerAgent:
    """Create practical plans with the local AI Core or a safe fallback."""

    def __init__(self, ai_core: AICore | None = None) -> None:
        self.ai_core = ai_core or AICore()

    def create_plan(self, goal: str, model: str = DEFAULT_MODEL) -> PlanDraft:
        """Create a plan draft for a goal."""
        goal = goal.strip()
        if not goal:
            return self._fallback_plan(goal)

        try:
            if self.ai_core.is_available():
                response = self.ai_core.respond(
                    self._planner_message(goal),
                    model=model,
                )
                steps = self.parse_steps(response)
                if steps:
                    return PlanDraft(
                        summary=f"Execution plan for: {goal}",
                        steps=steps,
                        fallback_used=False,
                    )
        except Exception:
            pass

        return self._fallback_plan(goal)

    def parse_steps(self, text: str) -> list[dict]:
        """Parse numbered planner output into step dictionaries."""
        if not text:
            return []

        steps = []
        for line in text.splitlines():
            match = re.match(r"^\s*\d+[\.\)]\s+(.+?)\s*$", line)
            if not match:
                continue

            title, details = self._split_step(match.group(1))
            if title:
                steps.append({"title": title, "details": details})

        if len(steps) < 5:
            return []

        return steps[:8]

    def _planner_message(self, goal: str) -> str:
        return f"{PLANNER_PROMPT}\n\nGoal: {goal}"

    def _fallback_plan(self, goal: str) -> PlanDraft:
        return PlanDraft(
            summary=f"Starter plan for: {goal or 'the goal'}",
            steps=[{"title": title, "details": ""} for title in FALLBACK_STEPS],
            fallback_used=True,
        )

    def _split_step(self, text: str) -> tuple[str, str]:
        title, separator, details = text.partition(" - ")
        if not separator:
            return text.strip(), ""

        return title.strip(), details.strip()
