"""Status reporting for Axion."""

from __future__ import annotations

import platform
from pathlib import Path

from axion.core.identity import AXION_VERSION
from axion.memory.sqlite_memory import SQLiteMemory


def build_status(
    memory: SQLiteMemory, current_model: str, ollama_available: bool
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
            f"Current directory: {Path.cwd()}",
            f"Python: {platform.python_version()}",
        ]
    )
