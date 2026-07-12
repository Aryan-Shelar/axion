"""Tests for Smart Organizer command routing."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from axion.commands.router import CommandRouter
from axion.memory.sqlite_memory import SQLiteMemory
from axion.projects.project_store import ProjectStore
from axion.tasks.task_store import TaskStore
from axion.tools.organizer import OrganizerResult


class FakeAICore:
    def is_available(self) -> bool:
        return False


class FakeOrganizer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def scan(self, target: str) -> OrganizerResult:
        self.calls.append(("scan", target))
        return OrganizerResult("scan ok", True, 2)

    def preview(self) -> OrganizerResult:
        self.calls.append(("preview", None))
        return OrganizerResult("preview ok", True, 2)

    def apply(self, confirm: bool = False) -> OrganizerResult:
        self.calls.append(("apply", confirm))
        if confirm:
            return OrganizerResult("apply ok", True, 2)
        return OrganizerResult("blocked", False, 0)

    def undo_last(self) -> OrganizerResult:
        self.calls.append(("undo_last", None))
        return OrganizerResult("undo ok", True, 2)

    def status(self) -> OrganizerResult:
        self.calls.append(("status", None))
        return OrganizerResult("status ok")

    def clear(self) -> OrganizerResult:
        self.calls.append(("clear", None))
        return OrganizerResult("clear ok")


class RouterOrganizerTests(unittest.TestCase):
    @patch("axion.commands.router.log_activity")
    def test_organize_commands_route_to_organizer(self, mock_log_activity) -> None:
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "axion.db"
            organizer = FakeOrganizer()
            router = CommandRouter(
                memory=SQLiteMemory(db_path),
                ai_core=FakeAICore(),
                task_store=TaskStore(db_path),
                project_store=ProjectStore(db_path),
                organizer=organizer,
            )

            scan = router.handle("/organize scan downloads")
            preview = router.handle("/organize preview")
            blocked = router.handle("/organize apply")
            applied = router.handle("/organize apply --confirm")
            undone = router.handle("/organize undo-last")
            status = router.handle("/organize status")
            cleared = router.handle("/organize clear")

        self.assertEqual(scan.message, "scan ok")
        self.assertEqual(preview.message, "preview ok")
        self.assertEqual(blocked.message, "blocked")
        self.assertEqual(applied.message, "apply ok")
        self.assertEqual(undone.message, "undo ok")
        self.assertEqual(status.message, "status ok")
        self.assertEqual(cleared.message, "clear ok")
        self.assertEqual(
            organizer.calls,
            [
                ("scan", "downloads"),
                ("preview", None),
                ("apply", False),
                ("apply", True),
                ("undo_last", None),
                ("status", None),
                ("clear", None),
            ],
        )
        mock_log_activity.assert_any_call("organizer scan completed", "downloads")
        mock_log_activity.assert_any_call("organizer preview shown", "count=2")
        mock_log_activity.assert_any_call("organizer apply blocked", "blocked")
        mock_log_activity.assert_any_call("organizer apply completed", "moved=2")
        mock_log_activity.assert_any_call("organizer undo completed", "undone=2")
        mock_log_activity.assert_any_call("organizer cleared")


if __name__ == "__main__":
    unittest.main()
