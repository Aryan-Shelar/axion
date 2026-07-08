"""SQLite-backed project storage for Axion."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from axion.memory.sqlite_memory import DEFAULT_DB_PATH


PROJECT_STATUSES = {"active", "paused", "done"}


@dataclass(frozen=True)
class ProjectItem:
    """A saved project row."""

    id: int
    name: str
    description: str | None
    status: str
    folder_path: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ProjectNoteItem:
    """A saved project note row."""

    id: int
    project_id: int
    content: str
    created_at: str


class ProjectStore:
    """Store projects and project notes in the local SQLite database."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        """Create project tables if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    folder_path TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS project_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
                """
            )

    def create_project(self, name: str, description: str | None = None) -> int:
        """Create a project and return its new id."""
        timestamp = self._timestamp()

        try:
            with self._connection() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO projects (
                        name, description, status, folder_path, created_at, updated_at
                    )
                    VALUES (?, ?, 'active', NULL, ?, ?)
                    """,
                    (name, description, timestamp, timestamp),
                )
                return int(cursor.lastrowid)
        except sqlite3.IntegrityError as error:
            raise ValueError(f"A project named '{name}' already exists.") from error

    def list_projects(self, status: str | None = None) -> list[ProjectItem]:
        """Return projects, optionally filtered by status."""
        if status:
            self._validate_status(status)
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, name, description, status, folder_path, created_at, updated_at
                    FROM projects
                    WHERE status = ?
                    ORDER BY id ASC
                    """,
                    (status,),
                ).fetchall()
        else:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, name, description, status, folder_path, created_at, updated_at
                    FROM projects
                    ORDER BY id ASC
                    """
                ).fetchall()

        return [self._project_from_row(row) for row in rows]

    def get_project(self, identifier: str) -> ProjectItem | None:
        """Get a project by id or exact project name."""
        cleaned_identifier = identifier.strip()
        if not cleaned_identifier:
            return None

        if cleaned_identifier.isdigit():
            query = (
                "SELECT id, name, description, status, folder_path, "
                "created_at, updated_at FROM projects WHERE id = ?"
            )
            parameters = (int(cleaned_identifier),)
        else:
            query = (
                "SELECT id, name, description, status, folder_path, "
                "created_at, updated_at FROM projects WHERE name = ?"
            )
            parameters = (cleaned_identifier,)

        with self._connection() as connection:
            row = connection.execute(query, parameters).fetchone()

        if row is None:
            return None

        return self._project_from_row(row)

    def update_project_status(self, identifier: str, status: str) -> bool:
        """Update a project's status. Return True if a row changed."""
        self._validate_status(status)
        project = self.get_project(identifier)
        if project is None:
            return False

        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE projects
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, self._timestamp(), project.id),
            )
            return cursor.rowcount > 0

    def set_project_folder(self, identifier: str, folder_path: str) -> bool:
        """Save a folder path for a project."""
        project = self.get_project(identifier)
        if project is None:
            return False

        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE projects
                SET folder_path = ?, updated_at = ?
                WHERE id = ?
                """,
                (folder_path, self._timestamp(), project.id),
            )
            return cursor.rowcount > 0

    def add_project_note(self, identifier: str, content: str) -> int | None:
        """Save a project note. Return the note id, or None if not found."""
        project = self.get_project(identifier)
        if project is None:
            return None

        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO project_notes (project_id, content, created_at)
                VALUES (?, ?, ?)
                """,
                (project.id, content, self._timestamp()),
            )
            return int(cursor.lastrowid)

    def list_project_notes(self, identifier: str) -> list[ProjectNoteItem] | None:
        """Return notes for a project, or None if the project is not found."""
        project = self.get_project(identifier)
        if project is None:
            return None

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT id, project_id, content, created_at
                FROM project_notes
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project.id,),
            ).fetchall()

        return [
            ProjectNoteItem(
                id=row[0],
                project_id=row[1],
                content=row[2],
                created_at=row[3],
            )
            for row in rows
        ]

    def count_projects(self, status: str | None = None) -> int:
        """Return the number of projects, optionally filtered by status."""
        if status:
            self._validate_status(status)
            with self._connection() as connection:
                row = connection.execute(
                    "SELECT COUNT(*) FROM projects WHERE status = ?",
                    (status,),
                ).fetchone()
        else:
            with self._connection() as connection:
                row = connection.execute("SELECT COUNT(*) FROM projects").fetchone()

        return int(row[0])

    def _validate_status(self, status: str) -> None:
        if status not in PROJECT_STATUSES:
            allowed_statuses = ", ".join(sorted(PROJECT_STATUSES))
            raise ValueError(f"Status must be one of: {allowed_statuses}")

    def _project_from_row(self, row: tuple) -> ProjectItem:
        return ProjectItem(
            id=row[0],
            name=row[1],
            description=row[2],
            status=row[3],
            folder_path=row[4],
            created_at=row[5],
            updated_at=row[6],
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
