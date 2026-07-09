"""Tests for app-level voice mode behavior."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from axion.core.app import AxionApp
from axion.voice.speaker import VoiceResult


class AppVoiceTests(unittest.TestCase):
    @patch("axion.core.app.log_activity")
    @patch("axion.core.app.speak_text")
    def test_normal_reply_can_be_spoken(self, mock_speak_text, mock_log_activity) -> None:
        mock_speak_text.return_value = VoiceResult(True, "Spoken.")
        app = AxionApp()

        app._speak_normal_reply("Hello from Axion.")

        mock_speak_text.assert_called_once_with("Hello from Axion.")
        mock_log_activity.assert_any_call("voice spoken", "normal chat reply")


if __name__ == "__main__":
    unittest.main()
