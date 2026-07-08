"""Safe allowlisted app launcher for Axion."""

from __future__ import annotations

import subprocess


APP_SHORTCUTS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "vscode": "code",
    "cmd": "cmd.exe",
    "explorer": "explorer.exe",
}


def list_app_shortcuts() -> list[str]:
    """Return available app shortcuts in a stable order."""
    return sorted(APP_SHORTCUTS)


def launch_app(app_name: str) -> tuple[str, bool]:
    """Launch an allowlisted app by shortcut name."""
    shortcut = app_name.strip().lower()
    if shortcut not in APP_SHORTCUTS:
        return "Unknown app. Type /apps to see available apps.", False

    command = APP_SHORTCUTS[shortcut]

    try:
        subprocess.Popen([command], shell=False)
    except OSError as error:
        return f"I could not open {shortcut}: {error}", False

    return f"Opening {shortcut}...", True
