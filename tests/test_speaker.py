"""Tests for Axion voice output."""

from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from axion.voice.speaker import speak_text


class SpeakerTests(unittest.TestCase):
    @patch("axion.voice.speaker.subprocess.run")
    @patch("axion.voice.speaker.platform.system")
    def test_speak_text_uses_powershell_with_shell_false(
        self, mock_system, mock_run
    ) -> None:
        mock_system.return_value = "Windows"
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="",
            stderr="",
        )

        result = speak_text("Hello Shelar")

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Spoken.")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0][0], "powershell")
        self.assertIn("System.Speech.Synthesis", args[0][5])
        self.assertEqual(kwargs["env"]["AXION_SPEAK_TEXT"], "Hello Shelar")
        self.assertIs(kwargs["shell"], False)

    @patch("axion.voice.speaker.subprocess.run")
    @patch("axion.voice.speaker.platform.system")
    def test_speak_text_is_windows_only(self, mock_system, mock_run) -> None:
        mock_system.return_value = "Linux"

        result = speak_text("Hello")

        self.assertFalse(result.success)
        self.assertIn("Windows", result.message)
        mock_run.assert_not_called()

    @patch("axion.voice.speaker.subprocess.run")
    @patch("axion.voice.speaker.platform.system")
    def test_speak_text_returns_friendly_error(self, mock_system, mock_run) -> None:
        mock_system.return_value = "Windows"
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="speech failed",
        )

        result = speak_text("Hello")

        self.assertFalse(result.success)
        self.assertEqual(result.message, "Voice output failed: speech failed")


if __name__ == "__main__":
    unittest.main()
