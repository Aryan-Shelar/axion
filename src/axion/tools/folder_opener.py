"""Open local folders from Axion commands."""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


HOME_FOLDER_ALIASES = {
    "desktop": "Desktop",
    "documents": "Documents",
    "downloads": "Downloads",
    "music": "Music",
    "pictures": "Pictures",
    "videos": "Videos",
}


def open_folder(path_text: str) -> str:
    """Validate and open a folder, returning a user-friendly message."""
    try:
        folder_path = resolve_folder_path(path_text)
    except (OSError, ValueError) as error:
        return f"I could not understand that folder path: {error}"

    if not folder_path.exists():
        return f"I could not find that folder: {folder_path}"

    if not folder_path.is_dir():
        return "This path exists, but it is not a folder."

    try:
        open_folder_path(folder_path)
    except (OSError, subprocess.CalledProcessError) as error:
        return f"I could not open that folder: {error}"

    return f"Opened folder: {folder_path}"


def resolve_folder_path(path_text: str) -> Path:
    """Resolve shortcuts and user paths into an absolute Path."""
    cleaned_path = path_text.strip()
    shortcut = HOME_FOLDER_ALIASES.get(cleaned_path.lower())

    if shortcut:
        path = Path.home() / shortcut
    else:
        path = Path(cleaned_path).expanduser()

    return path.resolve(strict=False)


def open_folder_path(folder_path: Path) -> None:
    """Open a folder using the current operating system."""
    system_name = platform.system()

    if system_name == "Windows":
        os.startfile(str(folder_path))  # type: ignore[attr-defined]
        return

    if system_name == "Darwin":
        subprocess.run(["open", str(folder_path)], check=True)
        return

    subprocess.run(["xdg-open", str(folder_path)], check=True)
