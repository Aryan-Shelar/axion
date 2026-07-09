"""Tests for the /run command router integration."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from axion.commands.router import CommandRouter
from axion.memory.sqlite_memory import SQLiteMemory
from axion.projects.project_store import ProjectStore
from axion.tasks.task_store import TaskStore
from axion.tools.safe_runner import SafeCommandResult


class FakeAICore:
    def is_available(self) -> bool:
        return False


class RouterRunTests(unittest.TestCase):
    @patch("axion.commands.router.log_activity")
    @patch("axion.commands.router.run_safe_command")
    def test_run_command_routes_to_safe_runner(
        self, mock_run_safe_command, mock_log_activity
    ) -> None:
        mock_run_safe_command.return_value = SafeCommandResult("ok", "executed")

        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "axion.db"
            router = CommandRouter(
                memory=SQLiteMemory(db_path),
                ai_core=FakeAICore(),
                task_store=TaskStore(db_path),
                project_store=ProjectStore(db_path),
            )

            response = router.handle("/run git status")

        self.assertEqual(response.message, "ok")
        self.assertFalse(response.should_exit)
        mock_run_safe_command.assert_called_once_with("git status")
        mock_log_activity.assert_any_call("command used", "/run")
        mock_log_activity.assert_any_call("safe command executed", "git status")


if __name__ == "__main__":
    unittest.main()
