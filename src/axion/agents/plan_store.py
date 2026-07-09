"""SQLite-backed storage for Agent Mode plans."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from axion.memory.sqlite_memory import DEFAULT_DB_PATH


PLAN_STATUSES = {"active", "paused", "done"}
STEP_STATUSES = {"open", "done"}


@dataclass(frozen=True)
class PlanItem:
    """A saved agent plan."""

    id: int
    goal: str
    summary: str | None
    status: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class PlanStep:
    """A saved step inside an agent plan."""

    id: int
    plan_id: int
    step_number: int
    title: str
    details: str | None
    status: str
    created_at: str
    completed_at: str | None


class PlanStore:
    """Store Agent Mode plans and steps in Axion's SQLite database."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        """Create agent plan tables if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal TEXT NOT NULL,
                    summary TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER NOT NULL,
                    step_number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    details TEXT,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    FOREIGN KEY (plan_id) REFERENCES agent_plans (id)
                )
                """
            )

    def create_plan(self, goal: str, summary: str, steps: list[dict]) -> int:
        """Create a plan and its ordered steps. Return the new plan id."""
        timestamp = self._timestamp()

        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO agent_plans (goal, summary, status, created_at, updated_at)
                VALUES (?, ?, 'active', ?, ?)
                """,
                (goal, summary, timestamp, timestamp),
            )
            plan_id = int(cursor.lastrowid)

            for index, step in enumerate(steps, start=1):
                connection.execute(
                    """
                    INSERT INTO agent_steps (
                        plan_id, step_number, title, details, status, created_at, completed_at
                    )
                    VALUES (?, ?, ?, ?, 'open', ?, NULL)
                    """,
                    (
                        plan_id,
                        index,
                        str(step.get("title", "")).strip(),
                        str(step.get("details", "")).strip() or None,
                        timestamp,
                    ),
                )

            return plan_id

    def list_plans(self, status: str | None = None) -> list[PlanItem]:
        """Return plans, optionally filtered by status."""
        if status:
            self._validate_plan_status(status)
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, goal, summary, status, created_at, updated_at
                    FROM agent_plans
                    WHERE status = ?
                    ORDER BY id ASC
                    """,
                    (status,),
                ).fetchall()
        else:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, goal, summary, status, created_at, updated_at
                    FROM agent_plans
                    ORDER BY id ASC
                    """
                ).fetchall()

        return [self._plan_from_row(row) for row in rows]

    def get_plan(self, plan_id: int) -> PlanItem | None:
        """Return one plan by id."""
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT id, goal, summary, status, created_at, updated_at
                FROM agent_plans
                WHERE id = ?
                """,
                (plan_id,),
            ).fetchone()

        if row is None:
            return None

        return self._plan_from_row(row)

    def list_steps(self, plan_id: int) -> list[PlanStep]:
        """Return ordered steps for a plan."""
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT id, plan_id, step_number, title, details, status, created_at, completed_at
                FROM agent_steps
                WHERE plan_id = ?
                ORDER BY step_number ASC
                """,
                (plan_id,),
            ).fetchall()

        return [self._step_from_row(row) for row in rows]

    def mark_step_done(self, plan_id: int, step_number: int) -> bool:
        """Mark a plan step as done. Return True if a row changed."""
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE agent_steps
                SET status = 'done', completed_at = ?
                WHERE plan_id = ? AND step_number = ?
                """,
                (self._timestamp(), plan_id, step_number),
            )
            return cursor.rowcount > 0

    def update_plan_status(self, plan_id: int, status: str) -> bool:
        """Update a plan's status. Return True if a row changed."""
        self._validate_plan_status(status)
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE agent_plans
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, self._timestamp(), plan_id),
            )
            return cursor.rowcount > 0

    def count_plans(self, status: str | None = None) -> int:
        """Return the number of plans, optionally filtered by status."""
        if status:
            self._validate_plan_status(status)
            with self._connection() as connection:
                row = connection.execute(
                    "SELECT COUNT(*) FROM agent_plans WHERE status = ?",
                    (status,),
                ).fetchone()
        else:
            with self._connection() as connection:
                row = connection.execute("SELECT COUNT(*) FROM agent_plans").fetchone()

        return int(row[0])

    def get_active_plan_context(self, limit: int = 3) -> list[str]:
        """Return compact active plan context for the AI Core."""
        context_lines = []
        for plan in self.list_plans("active")[:limit]:
            next_step = self._next_open_step(plan.id)
            if next_step:
                context_lines.append(
                    f"Plan {plan.id}: {plan.goal}\n  Next step: {next_step.title}"
                )
            else:
                context_lines.append(f"Plan {plan.id}: {plan.goal}\n  Next step: none")

        return context_lines

    def _next_open_step(self, plan_id: int) -> PlanStep | None:
        for step in self.list_steps(plan_id):
            if step.status == "open":
                return step

        return None

    def _validate_plan_status(self, status: str) -> None:
        if status not in PLAN_STATUSES:
            allowed_statuses = ", ".join(sorted(PLAN_STATUSES))
            raise ValueError(f"Status must be one of: {allowed_statuses}")

    def _plan_from_row(self, row: tuple) -> PlanItem:
        return PlanItem(
            id=row[0],
            goal=row[1],
            summary=row[2],
            status=row[3],
            created_at=row[4],
            updated_at=row[5],
        )

    def _step_from_row(self, row: tuple) -> PlanStep:
        return PlanStep(
            id=row[0],
            plan_id=row[1],
            step_number=row[2],
            title=row[3],
            details=row[4],
            status=row[5],
            created_at=row[6],
            completed_at=row[7],
        )

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
