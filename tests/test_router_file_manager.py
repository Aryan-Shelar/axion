"""Tests for file manager command routing."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from axion.commands.router import CommandRouter
from axion.memory.sqlite_memory import SQLiteMemory
from axion.projects.project_store import ProjectStore
from axion.tasks.task_store import TaskStore
from axion.tools.file_manager import FileManagerResult


class FakeAICore:
    def is_available(self) -> bool:
        return False


class RouterFileManagerTests(unittest.TestCase):
    @patch("axion.commands.router.log_activity")
    @patch("axion.commands.router.search_files")
    def test_find_command_routes_to_file_search(
        self, mock_search_files, mock_log_activity
    ) -> None:
        mock_search_files.return_value = FileManagerResult("found", True, "count=1")

        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "axion.db"
            router = CommandRouter(
                memory=SQLiteMemory(db_path),
                ai_core=FakeAICore(),
                task_store=TaskStore(db_path),
                project_store=ProjectStore(db_path),
            )

            response = router.handle("/find axion in D:\\Axion")

        self.assertEqual(response.message, "found")
        mock_search_files.assert_called_once_with("axion", "D:\\Axion")
        mock_log_activity.assert_any_call("command used", "/find")
        mock_log_activity.assert_any_call("file search started", "axion in D:\\Axion")
        mock_log_activity.assert_any_call("file search completed", "count=1")

    @patch("axion.commands.router.log_activity")
    @patch("axion.commands.router.trash_file")
    def test_trash_command_routes_to_file_manager(
        self, mock_trash_file, mock_log_activity
    ) -> None:
        mock_trash_file.return_value = FileManagerResult(
            "File moved to Axion Trash: D:\\Axion\\data\\trash\\x\\test.png",
            True,
            "D:\\Axion\\data\\trash\\x\\test.png",
        )

        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "axion.db"
            router = CommandRouter(
                memory=SQLiteMemory(db_path),
                ai_core=FakeAICore(),
                task_store=TaskStore(db_path),
                project_store=ProjectStore(db_path),
            )

            response = router.handle("/trash C:\\Users\\ADMIN\\Downloads\\test.png")

        self.assertIn("File moved to Axion Trash", response.message)
        mock_trash_file.assert_called_once_with("C:\\Users\\ADMIN\\Downloads\\test.png")
        mock_log_activity.assert_any_call("command used", "/trash")
        mock_log_activity.assert_any_call(
            "file trashed",
            "D:\\Axion\\data\\trash\\x\\test.png",
        )


if __name__ == "__main__":
    unittest.main()
