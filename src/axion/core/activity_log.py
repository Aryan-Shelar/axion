"""Activity logging for Axion."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_PATH = LOG_DIR / "axion.log"


def log_activity(event: str, detail: str = "") -> None:
    """Append a simple activity entry to the Axion log file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"{timestamp} | {event}"

    if detail:
        line = f"{line} | {detail}"

    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{line}\n")
