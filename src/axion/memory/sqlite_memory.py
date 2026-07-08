"""SQLite-backed memory and notes storage for Axion."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "axion.db"


@dataclass(frozen=True)
class MemoryItem:
    """A saved memory row."""

    id: int
    content: str
    created_at: str


@dataclass(frozen=True)
class NoteItem:
    """A saved note row."""

    id: int
    title: str
    content: str
    created_at: str


class SQLiteMemory:
    """Store Axion memories and notes in a local SQLite database."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        """Create the database and tables if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def add_memory(self, content: str) -> int:
        """Save a memory and return its new id."""
        created_at = self._timestamp()

        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO memories (content, created_at) VALUES (?, ?)",
                (content, created_at),
            )
            return int(cursor.lastrowid)

    def list_memories(self) -> list[MemoryItem]:
        """Return all memories, newest first."""
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT id, content, created_at FROM memories ORDER BY id DESC"
            ).fetchall()

        return [MemoryItem(id=row[0], content=row[1], created_at=row[2]) for row in rows]

    def count_memories(self) -> int:
        """Return the number of saved memories."""
        with self._connection() as connection:
            row = connection.execute("SELECT COUNT(*) FROM memories").fetchone()

        return int(row[0])

    def search_memories(self, keyword: str) -> list[MemoryItem]:
        """Return memories that contain the keyword, newest first."""
        pattern = f"%{keyword}%"
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT id, content, created_at
                FROM memories
                WHERE content LIKE ?
                ORDER BY id DESC
                """,
                (pattern,),
            ).fetchall()

        return [MemoryItem(id=row[0], content=row[1], created_at=row[2]) for row in rows]

    def add_note(self, title: str, content: str) -> int:
        """Save a note and return its new id."""
        created_at = self._timestamp()

        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)",
                (title, content, created_at),
            )
            return int(cursor.lastrowid)

    def list_notes(self) -> list[NoteItem]:
        """Return all notes, newest first."""
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT id, title, content, created_at FROM notes ORDER BY id DESC"
            ).fetchall()

        return [
            NoteItem(id=row[0], title=row[1], content=row[2], created_at=row[3])
            for row in rows
        ]

    def count_notes(self) -> int:
        """Return the number of saved notes."""
        with self._connection() as connection:
            row = connection.execute("SELECT COUNT(*) FROM notes").fetchone()

        return int(row[0])

    def search_notes(self, keyword: str) -> list[NoteItem]:
        """Return notes that contain the keyword in the title or content."""
        pattern = f"%{keyword}%"
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT id, title, content, created_at
                FROM notes
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY id DESC
                """,
                (pattern, pattern),
            ).fetchall()

        return [
            NoteItem(id=row[0], title=row[1], content=row[2], created_at=row[3])
            for row in rows
        ]

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
