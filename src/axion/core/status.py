"""Build Axion status output."""

from __future__ import annotations

from pathlib import Path

from axion.core.identity import AXION_VERSION
from axion.memory.sqlite_memory import DEFAULT_DB_PATH


def _safe_count(store: object, method_name: str, *args: object) -> int:
    """Call a count method safely and return 0 if unavailable."""
    try:
        method = getattr(store, method_name)
        return int(method(*args))
    except Exception:
        return 0


def build_status(
    memory,
    current_model: str,
    ollama_available: bool,
    task_store=None,
    project_store=None,
    voice_enabled: bool = False,
    plan_store=None,
) -> str:
    """Return a human-readable Axion system status."""
    lines = [
        "Axion status:",
        f"Version: {AXION_VERSION}",
        "AI Provider: Ollama",
        f"Current model: {current_model}",
        f"Ollama available: {'yes' if ollama_available else 'no'}",
        "Safe terminal runner: enabled",
        "File manager: enabled",
        "Browser research: enabled",
        f"Voice output: {'enabled' if voice_enabled else 'disabled'}",
        "Agent mode: enabled",
        f"Axion trash folder: {Path('data/trash').resolve()}",
        f"Memory database: {DEFAULT_DB_PATH.resolve()}",
    ]

    lines.extend(
        [
            f"Memories: {_safe_count(memory, 'count_memories')}",
            f"Notes: {_safe_count(memory, 'count_notes')}",
        ]
    )

    if task_store is not None:
        lines.extend(
            [
                f"Open tasks: {_safe_count(task_store, 'count_tasks', 'open')}",
                f"Done tasks: {_safe_count(task_store, 'count_tasks', 'done')}",
            ]
        )

    if project_store is not None:
        lines.extend(
            [
                f"Active projects: {_safe_count(project_store, 'count_projects', 'active')}",
                f"Paused projects: {_safe_count(project_store, 'count_projects', 'paused')}",
                f"Done projects: {_safe_count(project_store, 'count_projects', 'done')}",
            ]
        )

    if plan_store is not None:
        lines.extend(
            [
                f"Active plans: {_safe_count(plan_store, 'count_plans', 'active')}",
                f"Paused plans: {_safe_count(plan_store, 'count_plans', 'paused')}",
                f"Done plans: {_safe_count(plan_store, 'count_plans', 'done')}",
            ]
        )

    lines.extend(
        [
            f"Current directory: {Path.cwd()}",
            f"Python: {__import__('platform').python_version()}",
        ]
    )

    return "\n".join(lines)
