"""Run a small set of safe terminal commands.

The runner uses an exact allowlist and never passes user input through a shell.
This keeps v0.6 useful for status checks without turning Axion into an
arbitrary command executor.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
import subprocess


BLOCKED_MESSAGE = "Blocked for safety."
REJECTED_MESSAGE = (
    "Command not allowed yet. Axion only supports safe allowlisted commands."
)

BLOCKED_KEYWORDS = {
    "del",
    "erase",
    "rmdir",
    "rd",
    "format",
    "shutdown",
    "restart",
    "powershell",
    "rm",
    "remove-item",
    "taskkill",
}

TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class SafeCommandResult:
    """Result returned by the safe command runner."""

    message: str
    status: str


def run_safe_command(command_text: str) -> SafeCommandResult:
    """Run an allowlisted command and return a user-friendly result."""
    normalized_command = _normalize_command(command_text)
    if not normalized_command:
        return SafeCommandResult("Usage: /run <command>", "rejected")

    if _contains_blocked_keyword(normalized_command):
        return SafeCommandResult(BLOCKED_MESSAGE, "blocked")

    command_args = _allowed_command_args(normalized_command)
    if command_args is None:
        return SafeCommandResult(REJECTED_MESSAGE, "rejected")

    try:
        completed = subprocess.run(
            command_args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            timeout=TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return SafeCommandResult(
            "I could not run that command because the program was not found.",
            "executed",
        )
    except subprocess.TimeoutExpired:
        return SafeCommandResult(
            f"Command timed out after {TIMEOUT_SECONDS} seconds.",
            "executed",
        )
    except OSError as error:
        return SafeCommandResult(
            f"I could not run that command: {error}",
            "executed",
        )

    return SafeCommandResult(_format_completed_process(completed), "executed")


def _normalize_command(command_text: str) -> str:
    return " ".join(command_text.strip().lower().split())


def _contains_blocked_keyword(command_text: str) -> bool:
    tokens = set(re.findall(r"[a-z0-9_-]+", command_text.lower()))
    return any(keyword in tokens for keyword in BLOCKED_KEYWORDS)


def _allowed_command_args(command_text: str) -> list[str] | None:
    commands: dict[str, list[str]] = {
        "git status": ["git", "status"],
        "git branch": ["git", "branch"],
        "git log": ["git", "log"],
        "dir": _dir_command(),
        "python --version": ["python", "--version"],
        "python -m axion": ["python", "-m", "axion"],
        "ollama list": ["ollama", "list"],
        "ollama --version": ["ollama", "--version"],
    }
    return commands.get(command_text)


def _dir_command() -> list[str]:
    if os.name == "nt":
        return ["cmd.exe", "/d", "/c", "dir"]

    return ["dir"]


def _format_completed_process(completed: subprocess.CompletedProcess[str]) -> str:
    output_parts = []
    if completed.stdout.strip():
        output_parts.append(completed.stdout.strip())
    if completed.stderr.strip():
        output_parts.append(completed.stderr.strip())

    if not output_parts:
        output_parts.append("(No output.)")

    if completed.returncode != 0:
        output_parts.append(f"Exit code: {completed.returncode}")

    return "\n".join(output_parts)
