"""Tests for voice command routing."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from axion.commands.router import CommandRouter
from axion.memory.sqlite_memory import SQLiteMemory
from axion.projects.project_store import ProjectStore
from axion.tasks.task_store import TaskStore
from axion.voice.speaker import VoiceResult


class FakeAICore:
    def is_available(self) -> bool:
        return False


def make_router(db_path: Path) -> CommandRouter:
    return CommandRouter(
        memory=SQLiteMemory(db_path),
        ai_core=FakeAICore(),
        task_store=TaskStore(db_path),
        project_store=ProjectStore(db_path),
    )


class RouterVoiceTests(unittest.TestCase):
    @patch("axion.commands.router.log_activity")
    @patch("axion.commands.router.speak_text")
    def test_say_speaks_even_when_voice_mode_is_off(
        self, mock_speak_text, mock_log_activity
    ) -> None:
        mock_speak_text.return_value = VoiceResult("Spoken.", True)

        with TemporaryDirectory() as temp_dir:
            router = make_router(Path(temp_dir) / "axion.db")

            response = router.handle("/say Hello Shelar")

        self.assertEqual(response.message, "Spoken.")
        mock_speak_text.assert_called_once_with("Hello Shelar")
        mock_log_activity.assert_any_call("command used", "/say")
        mock_log_activity.assert_any_call("voice spoken", "Hello Shelar")

    @patch("axion.commands.router.log_activity")
    def test_voice_mode_can_turn_on_and_off(self, mock_log_activity) -> None:
        with TemporaryDirectory() as temp_dir:
            router = make_router(Path(temp_dir) / "axion.db")

            initial = router.handle("/voice")
            enabled = router.handle("/voice on")
            after_enabled = router.handle("/voice")
            disabled = router.handle("/voice off")

        self.assertEqual(initial.message, "Voice mode is off.")
        self.assertEqual(enabled.message, "Voice mode enabled.")
        self.assertEqual(after_enabled.message, "Voice mode is on.")
        self.assertEqual(disabled.message, "Voice mode disabled.")
        self.assertFalse(router.voice_enabled)
        mock_log_activity.assert_any_call("voice mode enabled")
        mock_log_activity.assert_any_call("voice mode disabled")


if __name__ == "__main__":
    unittest.main()
