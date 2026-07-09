"""Voice output module for Axion."""

from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass


@dataclass
class VoiceResult:
    """Result returned after trying to speak text."""

    success: bool
    message: str

    @property
    def ok(self) -> bool:
        return self.success


class Speaker:
    """Speak text aloud using the operating system's built-in tools."""

    def __init__(self) -> None:
        self.system = platform.system().lower()

    def speak(self, text: str) -> VoiceResult:
        """Speak text aloud and return a VoiceResult."""
        clean_text = text.strip()

        if not clean_text:
            return VoiceResult(False, "Nothing to speak.")

        if self.system == "windows":
            return self._speak_windows(clean_text)

        return VoiceResult(
            False,
            "Voice output is currently supported on Windows only.",
        )

    def _speak_windows(self, text: str) -> VoiceResult:
        """Speak text on Windows using PowerShell System.Speech safely."""
        command = (
            "Add-Type -AssemblyName System.Speech; "
            "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$speaker.Rate = 0; "
            "$speaker.Volume = 100; "
            "$speaker.Speak($env:AXION_SPEAK_TEXT); "
            "$speaker.Dispose();"
        )

        env = os.environ.copy()
        env["AXION_SPEAK_TEXT"] = text

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    command,
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except FileNotFoundError:
            return VoiceResult(False, "Voice output failed: PowerShell was not found.")
        except subprocess.TimeoutExpired:
            return VoiceResult(False, "Voice output failed: speaking took too long.")
        except Exception as error:
            return VoiceResult(False, f"Voice output failed: {error}")

        if result.returncode != 0:
            error_message = result.stderr.strip() or result.stdout.strip()
            return VoiceResult(False, f"Voice output failed: {error_message}")

        return VoiceResult(True, "Spoken.")


def speak_text(text: str) -> VoiceResult:
    """Convenience function used by Axion commands."""
    speaker = Speaker()
    return speaker.speak(text)