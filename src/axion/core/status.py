"""Status reporting for Axion."""

from __future__ import annotations

import platform
from pathlib import Path

from axion.core.identity import AXION_VERSION
from axion.memory.sqlite_memory import SQLiteMemory
from axion.projects.project_store import ProjectStore
from axion.tasks.task_store import TaskStore


def build_status(
    memory: SQLiteMemory,
    current_model: str,
    ollama_available: bool,
    task_store: TaskStore,
    project_store: ProjectStore,
) -> str:
    """Build a readable status report for the terminal."""
    available_text = "yes" if ollama_available else "no"

    return "\n".join(
        [
            "Axion status:",
            f"Version: {AXION_VERSION}",
            "AI Provider: Ollama",
            f"Current model: {current_model}",
            f"Ollama available: {available_text}",
            f"Memory database: {memory.db_path}",
            f"Memories: {memory.count_memories()}",
            f"Notes: {memory.count_notes()}",
            f"Open tasks: {task_store.count_tasks('open')}",
            f"Done tasks: {task_store.count_tasks('done')}",
            f"Active projects: {project_store.count_projects('active')}",
            f"Paused projects: {project_store.count_projects('paused')}",
            f"Done projects: {project_store.count_projects('done')}",
            f"Current directory: {Path.cwd()}",
            f"Python: {platform.python_version()}",
        ]
    )
