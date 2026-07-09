"""Tests for Axion's safe terminal runner."""

from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from axion.tools.safe_runner import (
    BLOCKED_MESSAGE,
    REJECTED_MESSAGE,
    run_safe_command,
)


class SafeRunnerTests(unittest.TestCase):
    @patch("axion.tools.safe_runner.subprocess.run")
    def test_allowlisted_command_runs_with_shell_false(self, mock_run) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["git", "status"],
            returncode=0,
            stdout="working tree clean\n",
            stderr="",
        )

        result = run_safe_command("git status")

        self.assertEqual(result.status, "executed")
        self.assertEqual(result.message, "working tree clean")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["git", "status"])
        self.assertIs(kwargs["shell"], False)

    @patch("axion.tools.safe_runner.subprocess.run")
    def test_blocked_keyword_does_not_run(self, mock_run) -> None:
        result = run_safe_command("del test.txt")

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.message, BLOCKED_MESSAGE)
        mock_run.assert_not_called()

    @patch("axion.tools.safe_runner.subprocess.run")
    def test_non_allowlisted_command_is_rejected(self, mock_run) -> None:
        result = run_safe_command("git checkout main")

        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.message, REJECTED_MESSAGE)
        mock_run.assert_not_called()

    @patch("axion.tools.safe_runner.subprocess.run")
    def test_stderr_is_returned_to_user(self, mock_run) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ollama", "list"],
            returncode=1,
            stdout="",
            stderr="ollama unavailable\n",
        )

        result = run_safe_command("ollama list")

        self.assertEqual(result.status, "executed")
        self.assertIn("ollama unavailable", result.message)
        self.assertIn("Exit code: 1", result.message)


if __name__ == "__main__":
    unittest.main()
