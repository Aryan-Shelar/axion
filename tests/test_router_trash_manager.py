"""Tests for Trash Manager command routing."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from axion.commands.router import CommandRouter
from axion.memory.sqlite_memory import SQLiteMemory
from axion.projects.project_store import ProjectStore
from axion.tasks.task_store import TaskStore
from axion.tools.trash_manager import TrashManager


class FakeAICore:
    def is_available(self) -> bool:
        return False


class RouterTrashManagerTests(unittest.TestCase):
    @patch("axion.commands.router.log_activity")
    def test_trash_commands_route_to_manager(self, mock_log_activity) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_path = root / "axion.db"
            trash_root = root / "trash"
            trashed_file = trash_root / "batch" / "restore.txt"
            trashed_file.parent.mkdir(parents=True)
            trashed_file.write_text("trashed", encoding="utf-8")
            destination = root / "Documents"
            destination.mkdir()
            trash_manager = TrashManager(trash_root)
            trash_id = trash_manager.record_trashed_file(
                str(root / "Downloads" / "restore.txt"),
                str(trashed_file),
            )

            router = CommandRouter(
                memory=SQLiteMemory(db_path),
                ai_core=FakeAICore(),
                task_store=TaskStore(db_path),
                project_store=ProjectStore(db_path),
                trash_manager=trash_manager,
            )

            listing = router.handle("/trash-list")
            detail = router.handle(f"/trash-show {trash_id}")
            preview = router.handle("/empty-trash preview")
            restored = router.handle(f"/restore {trash_id} :: {destination}")
            restored_exists = (destination / "restore.txt").exists()

        self.assertIn("restore.txt", listing.message)
        self.assertIn("Original path:", detail.message)
        self.assertIn("file(s) would be permanently deleted", preview.message)
        self.assertIn("Restored file to:", restored.message)
        self.assertTrue(restored_exists)
        mock_log_activity.assert_any_call("trash listed", "count=1")
        mock_log_activity.assert_any_call("trash item shown", f"id={trash_id}")
        mock_log_activity.assert_any_call("empty trash previewed", "count=1")
        mock_log_activity.assert_any_call("file restored", f"id={trash_id}")


if __name__ == "__main__":
    unittest.main()
