"""SQLite-backed task storage for Axion."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from axion.memory.sqlite_memory import DEFAULT_DB_PATH


@dataclass(frozen=True)
class TaskItem:
    """A saved task row."""

    id: int
    title: str
    status: str
    created_at: str
    completed_at: str | None


class TaskStore:
    """Store Axion tasks in the local SQLite database."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        """Create the tasks table if it does not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )

    def add_task(self, title: str) -> int:
        """Save a task and return its new id."""
        created_at = self._timestamp()

        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, status, created_at, completed_at)
                VALUES (?, 'open', ?, NULL)
                """,
                (title, created_at),
            )
            return int(cursor.lastrowid)

    def list_tasks(self, status: str | None = None) -> list[TaskItem]:
        """Return tasks, optionally filtered by status."""
        if status:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, title, status, created_at, completed_at
                    FROM tasks
                    WHERE status = ?
                    ORDER BY id ASC
                    """,
                    (status,),
                ).fetchall()
        else:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, title, status, created_at, completed_at
                    FROM tasks
                    ORDER BY id ASC
                    """
                ).fetchall()

        return [
            TaskItem(
                id=row[0],
                title=row[1],
                status=row[2],
                created_at=row[3],
                completed_at=row[4],
            )
            for row in rows
        ]

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as done. Return True if a row changed."""
        completed_at = self._timestamp()

        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET status = 'done', completed_at = ?
                WHERE id = ?
                """,
                (completed_at, task_id),
            )
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        """Delete a task from Axion's own task table."""
        with self._connection() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def count_tasks(self, status: str | None = None) -> int:
        """Return the number of tasks, optionally filtered by status."""
        if status:
            with self._connection() as connection:
                row = connection.execute(
                    "SELECT COUNT(*) FROM tasks WHERE status = ?",
                    (status,),
                ).fetchone()
        else:
            with self._connection() as connection:
                row = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()

        return int(row[0])

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """Open, commit, and close a SQLite connection."""
        connection = sqlite3.connect(self.db_path)
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _timestamp(self) -> str:
        return datetime.now().isoformat(timespec="seconds")
