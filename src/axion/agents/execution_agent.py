"""Safe Agent Execution Mode for Axion."""

from __future__ import annotations

from dataclasses import dataclass

from axion.agents.plan_store import PlanStore, PlanStep
from axion.projects.project_store import ProjectStore
from axion.tasks.task_store import TaskStore
from axion.tools.app_launcher import launch_app
from axion.tools.folder_opener import open_folder
from axion.tools.safe_runner import run_safe_command
from axion.tools.web_research import open_google_search


@dataclass(frozen=True)
class ExecutionResult:
    message: str
    success: bool = True


@dataclass(frozen=True)
class SuggestedAction:
    kind: str
    command: str
    description: str


class ExecutionAgent:
    """Preview and execute safe actions for the next open plan step."""

    def __init__(
        self,
        plan_store: PlanStore,
        task_store: TaskStore,
        project_store: ProjectStore,
    ) -> None:
        self.plan_store = plan_store
        self.task_store = task_store
        self.project_store = project_store

    def execute_next_step(self, plan_id: int, confirm: bool = False) -> ExecutionResult:
        plan = self.plan_store.get_plan(plan_id)
        if plan is None:
            return ExecutionResult(f"Plan {plan_id} was not found.", success=False)

        step = self._next_open_step(plan_id)
        if step is None:
            return ExecutionResult(f"All steps are already done for plan {plan_id}.")

        action = self._suggest_action(step)

        if not confirm:
            return ExecutionResult(self._format_preview(plan_id, step, action))

        return self._execute_action(plan_id, step, action)

    def _next_open_step(self, plan_id: int) -> PlanStep | None:
        for step in self.plan_store.list_steps(plan_id):
            if step.status == "open":
                return step
        return None

    def _suggest_action(self, step: PlanStep) -> SuggestedAction:
        text = f"{step.title} {step.details or ''}".lower()

        if any(word in text for word in ["git status", "check repository", "check repo"]):
            return SuggestedAction("safe_run", "/run git status", "Check repository status safely.")

        if any(word in text for word in ["open vscode", "open vs code", "code editor"]):
            return SuggestedAction("app", "/app vscode", "Open VS Code safely.")

        if any(word in text for word in ["open project", "project folder", "open axion"]):
            project = self.project_store.get_project("Axion")
            if project and project.folder_path:
                return SuggestedAction("project_open", "/project open Axion", "Open Axion project folder.")

        if any(word in text for word in ["research", "search", "find examples", "look up", "examples"]):
            return SuggestedAction("web_search", f"/web search {step.title}", "Open safe web search.")

        return SuggestedAction("task", f"/task add {step.title}", "Create an Axion task for this step.")

    def _format_preview(self, plan_id: int, step: PlanStep, action: SuggestedAction) -> str:
        details = f"\nDetails: {step.details}" if step.details else ""
        return "\n".join(
            [
                "Agent Execution Preview",
                f"Plan: {plan_id}",
                f"Next step: {step.step_number}. {step.title}{details}",
                "Suggested safe actions:",
                f"1. {action.command}",
                f"Reason: {action.description}",
                "",
                f"To execute, run: /agent execute {plan_id} --confirm",
            ]
        )

    def _execute_action(self, plan_id: int, step: PlanStep, action: SuggestedAction) -> ExecutionResult:
        messages = ["Executed:"]

        if action.kind == "task":
            task_id = self.task_store.add_task(f"Plan {plan_id}: {step.title}")
            messages.append(f"- Created task {task_id}: Plan {plan_id}: {step.title}")

        elif action.kind == "web_search":
            result = open_google_search(step.title)
            if not result.success:
                return ExecutionResult(result.message, success=False)
            messages.append(f"- {result.message}")

        elif action.kind == "project_open":
            project = self.project_store.get_project("Axion")
            if not project or not project.folder_path:
                task_id = self.task_store.add_task(f"Plan {plan_id}: {step.title}")
                messages.append(f"- Project folder unavailable. Created task {task_id}.")
            else:
                message = open_folder(project.folder_path)
                messages.append(f"- {message}")

        elif action.kind == "safe_run":
            result = run_safe_command("git status")
            if result.status != "executed":
                return ExecutionResult(result.message, success=False)
            messages.append(f"- {result.message}")

        elif action.kind == "app":
            message, launched = launch_app("vscode")
            if not launched:
                return ExecutionResult(message, success=False)
            messages.append(f"- {message}")

        else:
            task_id = self.task_store.add_task(f"Plan {plan_id}: {step.title}")
            messages.append(f"- Created task {task_id}: Plan {plan_id}: {step.title}")

        self.plan_store.mark_step_done(plan_id, step.step_number)
        messages.append(f"Plan {plan_id} step {step.step_number} marked done.")

        next_step = self._next_open_step(plan_id)
        if next_step:
            messages.append("")
            messages.append("Next step:")
            messages.append(f"{next_step.step_number}. {next_step.title}")
        else:
            messages.append("")
            messages.append(f"All steps are done for plan {plan_id}.")

        return ExecutionResult("\n".join(messages))
