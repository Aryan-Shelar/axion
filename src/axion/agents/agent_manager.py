"""Agent Mode orchestration for Axion."""

from __future__ import annotations

from dataclasses import dataclass

from axion.agents.plan_store import PLAN_STATUSES, PlanItem, PlanStep, PlanStore
from axion.agents.planner_agent import PlannerAgent
from axion.ai.ollama_client import DEFAULT_MODEL
from axion.tasks.task_store import TaskStore


@dataclass(frozen=True)
class AgentResult:
    """A user-facing Agent Mode result."""

    message: str
    success: bool = True
    plan_id: int | None = None
    fallback_used: bool = False
    count: int = 0


class AgentManager:
    """Create, format, and manage Agent Mode plans."""

    def __init__(
        self,
        plan_store: PlanStore,
        planner_agent: PlannerAgent | None = None,
        task_store: TaskStore | None = None,
    ) -> None:
        self.plan_store = plan_store
        self.planner_agent = planner_agent or PlannerAgent()
        self.task_store = task_store or TaskStore()

    def create_plan(self, goal: str, model: str = DEFAULT_MODEL) -> AgentResult:
        """Create, save, and format a plan for a goal."""
        goal = goal.strip()
        if not goal:
            return AgentResult("Usage: /agent plan <goal>", success=False)

        draft = self.planner_agent.create_plan(goal, model=model)
        plan_id = self.plan_store.create_plan(goal, draft.summary, draft.steps)
        plan = self.plan_store.get_plan(plan_id)
        steps = self.plan_store.list_steps(plan_id)

        return AgentResult(
            self.format_plan(plan, steps) if plan else f"Plan {plan_id} created.",
            success=True,
            plan_id=plan_id,
            fallback_used=draft.fallback_used,
        )

    def format_plan(self, plan: PlanItem, steps: list[PlanStep]) -> str:
        """Format one plan with its steps."""
        lines = [
            f"Plan {plan.id}:",
            f"Goal: {plan.goal}",
            f"Summary: {plan.summary or '(none)'}",
            f"Status: {plan.status}",
            "Steps:",
        ]
        for step in steps:
            details = f" - {step.details}" if step.details else ""
            lines.append(f"{step.step_number}. [{step.status}] {step.title}{details}")

        return "\n".join(lines)

    def format_plan_list(self, plans: list[PlanItem]) -> str:
        """Format a list of plans."""
        lines = ["Plans:"]
        for plan in plans:
            lines.append(f"{plan.id}. [{plan.status}] {plan.goal}")

        return "\n".join(lines)

    def next_step(self, plan_id: int) -> AgentResult:
        """Return the next open step for a plan."""
        plan = self.plan_store.get_plan(plan_id)
        if plan is None:
            return AgentResult(f"Plan {plan_id} was not found.", success=False)

        for step in self.plan_store.list_steps(plan_id):
            if step.status == "open":
                details = f"\nDetails: {step.details}" if step.details else ""
                return AgentResult(
                    f"Next step for plan {plan_id}:\n{step.step_number}. {step.title}{details}"
                )

        return AgentResult(f"All steps are done for plan {plan_id}.")

    def complete_step(self, plan_id: int, step_number: int) -> AgentResult:
        """Mark a plan step done."""
        if self.plan_store.get_plan(plan_id) is None:
            return AgentResult(f"Plan {plan_id} was not found.", success=False)

        if not self.plan_store.mark_step_done(plan_id, step_number):
            return AgentResult(
                f"Step {step_number} was not found for plan {plan_id}.",
                success=False,
            )

        return AgentResult(f"Plan {plan_id} step {step_number} marked done.")

    def set_plan_status(self, plan_id: int, status: str) -> AgentResult:
        """Set a plan status."""
        if status not in PLAN_STATUSES:
            return AgentResult(
                "Usage: /plan status <id> <active|paused|done>",
                success=False,
            )

        if not self.plan_store.update_plan_status(plan_id, status):
            return AgentResult(f"Plan {plan_id} was not found.", success=False)

        return AgentResult(f"Plan {plan_id} marked as {status}.")

    def convert_open_steps_to_tasks(self, plan_id: int) -> AgentResult:
        """Convert open plan steps into regular Axion tasks."""
        plan = self.plan_store.get_plan(plan_id)
        if plan is None:
            return AgentResult(f"Plan {plan_id} was not found.", success=False)

        open_steps = [
            step for step in self.plan_store.list_steps(plan_id) if step.status == "open"
        ]
        for step in open_steps:
            self.task_store.add_task(f"Plan {plan_id}: {step.title}")

        return AgentResult(
            f"Created {len(open_steps)} task(s) from plan {plan_id}.",
            success=True,
            plan_id=plan_id,
            count=len(open_steps),
        )
