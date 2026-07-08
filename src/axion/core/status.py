"""Status reporting for Axion."""

from __future__ import annotations

import platform
from pathlib import Path

from axion.core.identity import AXION_VERSION
from axion.memory.sqlite_memory import SQLiteMemory


def build_status(memory: SQLiteMemory) -> str:
    """Build a readable status report for the terminal."""
    return "\n".join(
        [
            "Axion status:",
            f"Version: {AXION_VERSION}",
            f"Memory database: {memory.db_path}",
            f"Memories: {memory.count_memories()}",
            f"Notes: {memory.count_notes()}",
            f"Current directory: {Path.cwd()}",
            f"Python: {platform.python_version()}",
        ]
    )
