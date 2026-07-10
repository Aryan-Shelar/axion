"""Safe file search, move, and trash helpers for Axion.

Axion never permanently deletes files. Trashing means moving a file into
Axion's local trash folder so the operation stays reversible.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from itertools import count
import os
from pathlib import Path
import shutil

from axion.tools.trash_manager import TrashManager


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRASH_ROOT = PROJECT_ROOT / "data" / "trash"

DEFAULT_SEARCH_LIMIT = 20
SCREENSHOT_PREVIEW_LIMIT = 30

SKIPPED_FOLDER_NAMES = {
    ".git",
    ".pnpm-store",
    ".venv",
    "__pycache__",
    "appdata",
    "node_modules",
    "program files",
    "program files (x86)",
    "windows",
}

SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SCREENSHOT_KEYWORDS = (
    "screenshot",
    "screen shot",
    "img_",
    "image",
    "capture",
)


@dataclass(frozen=True)
class FileManagerResult:
    """A file operation result that commands can print and log."""

    message: str
    success: bool
    detail: str = ""


def trash_root() -> Path:
    """Return the Axion trash root path."""
    TRASH_ROOT.mkdir(parents=True, exist_ok=True)
    return TRASH_ROOT


def search_files(
    query: str,
    folder: str | None = None,
    max_results: int = DEFAULT_SEARCH_LIMIT,
) -> FileManagerResult:
    """Search for files by filename, case-insensitively."""
    query = query.strip()
    if not query:
        return FileManagerResult("Usage: /find <query>", False)

    folders_result = _search_folders(folder)
    if not folders_result.success:
        return folders_result

    query_lower = query.lower()
    matches = []
    for path in _iter_files(folders_result.detail_paths):
        if query_lower in path.name.lower():
            matches.append(path)
            if len(matches) >= max_results:
                break

    if not matches:
        return FileManagerResult(f"No files found for: {query}", True)

    return FileManagerResult(
        _format_paths(f"Found files for '{query}':", matches),
        True,
        f"count={len(matches)}",
    )


def search_files_by_extension(
    extension: str,
    folder: str | None = None,
    max_results: int = DEFAULT_SEARCH_LIMIT,
) -> FileManagerResult:
    """Search for files by extension."""
    extension = extension.strip().lower()
    if not extension:
        return FileManagerResult("Usage: /find-ext <extension>", False)
    if not extension.startswith("."):
        extension = f".{extension}"
    if extension == ".":
        return FileManagerResult("Usage: /find-ext <extension>", False)

    folders_result = _search_folders(folder)
    if not folders_result.success:
        return folders_result

    matches = []
    for path in _iter_files(folders_result.detail_paths):
        if path.suffix.lower() == extension:
            matches.append(path)
            if len(matches) >= max_results:
                break

    if not matches:
        return FileManagerResult(f"No files found with extension: {extension}", True)

    return FileManagerResult(
        _format_paths(f"Found {extension} files:", matches),
        True,
        f"count={len(matches)}",
    )


def move_file(source_file_path: str, destination_folder: str) -> FileManagerResult:
    """Move one file into an existing folder without overwriting anything."""
    source = _path_from_user_text(source_file_path)
    destination = _path_from_user_text(destination_folder)

    validation = _validate_source_file(source)
    if validation:
        return validation

    if not destination.exists():
        return FileManagerResult(f"Destination folder not found: {destination}", False)
    if not destination.is_dir():
        return FileManagerResult("Destination must be a folder.", False)

    target = _safe_destination(destination, source.name)
    try:
        shutil.move(str(source), str(target))
    except OSError as error:
        return FileManagerResult(f"I could not move that file: {error}", False)

    return FileManagerResult(
        f"File moved to: {target}",
        True,
        str(target),
    )


def trash_file(file_path: str) -> FileManagerResult:
    """Move one file into Axion Trash."""
    source = _path_from_user_text(file_path)

    validation = _validate_source_file(source)
    if validation:
        return validation

    trash_folder = _new_trash_folder()
    result = _move_file_to_folder(source, trash_folder)
    if not result.success:
        return result

    _record_trash_metadata(source, result.detail)
    return FileManagerResult(
        f"File moved to Axion Trash: {result.detail}",
        True,
        result.detail,
    )


def preview_screenshots() -> FileManagerResult:
    """Preview screenshot-like files without moving anything."""
    screenshots = _find_screenshots(limit=SCREENSHOT_PREVIEW_LIMIT)
    if not screenshots:
        return FileManagerResult(
            "No screenshot-like files found in Desktop, Downloads, or Pictures.",
            True,
        )

    return FileManagerResult(
        _format_paths("Screenshot-like files:", screenshots),
        True,
        f"count={len(screenshots)}",
    )


def clean_screenshots(confirm: bool) -> FileManagerResult:
    """Move screenshot-like files into one timestamped Axion Trash folder."""
    if not confirm:
        return FileManagerResult(
            "Preview first with /screenshots preview. To clean, run /screenshots clean --confirm.",
            False,
        )

    screenshots = _find_screenshots(limit=None)
    if not screenshots:
        return FileManagerResult(
            "No screenshot-like files found to clean.",
            True,
        )

    trash_folder = _new_trash_folder()
    moved_count = 0
    failed_count = 0
    for screenshot in screenshots:
        result = _move_file_to_folder(screenshot, trash_folder)
        if result.success:
            _record_trash_metadata(screenshot, result.detail)
            moved_count += 1
        else:
            failed_count += 1

    if failed_count:
        return FileManagerResult(
            (
                f"Moved {moved_count} screenshot file(s) to Axion Trash: {trash_folder}\n"
                f"Could not move {failed_count} file(s)."
            ),
            False,
            str(trash_folder),
        )

    return FileManagerResult(
        f"Moved {moved_count} screenshot file(s) to Axion Trash: {trash_folder}",
        True,
        str(trash_folder),
    )


@dataclass(frozen=True)
class _FolderResult:
    success: bool
    detail_paths: list[Path]
    message: str = ""


def _search_folders(folder: str | None) -> _FolderResult | FileManagerResult:
    if folder:
        path = _path_from_user_text(folder)
        if not path.exists():
            return FileManagerResult(f"Folder not found: {path}", False)
        if not path.is_dir():
            return FileManagerResult(f"This path is not a folder: {path}", False)
        return _FolderResult(True, [path])

    folders = _default_search_locations()
    if not folders:
        return FileManagerResult("No search folders are available.", False)

    return _FolderResult(True, folders)


def _default_search_locations() -> list[Path]:
    home = Path.home()
    return _unique_existing_dirs(
        [
            Path.cwd(),
            home / "Downloads",
            home / "Documents",
            home / "Desktop",
            home / "Pictures",
        ]
    )


def _screenshot_locations() -> list[Path]:
    home = Path.home()
    return _unique_existing_dirs(
        [
            home / "Desktop",
            home / "Downloads",
            home / "Pictures",
        ]
    )


def _unique_existing_dirs(paths: list[Path]) -> list[Path]:
    seen = set()
    unique = []
    for path in paths:
        try:
            resolved = path.expanduser().resolve()
        except OSError:
            continue

        key = str(resolved).lower()
        if key in seen or not resolved.is_dir():
            continue

        seen.add(key)
        unique.append(resolved)

    return unique


def _iter_files(folders: list[Path]):
    for folder in folders:
        for root, dirnames, filenames in os.walk(folder, onerror=lambda error: None):
            dirnames[:] = [
                dirname
                for dirname in dirnames
                if dirname.lower() not in SKIPPED_FOLDER_NAMES
            ]
            root_path = Path(root)
            for filename in filenames:
                yield root_path / filename


def _find_screenshots(limit: int | None) -> list[Path]:
    matches = []
    for path in _iter_files(_screenshot_locations()):
        if not _is_screenshot_like(path):
            continue

        matches.append(path)
        if limit is not None and len(matches) >= limit:
            break

    return matches


def _is_screenshot_like(path: Path) -> bool:
    if path.suffix.lower() not in SCREENSHOT_EXTENSIONS:
        return False

    filename = path.name.lower()
    return any(keyword in filename for keyword in SCREENSHOT_KEYWORDS)


def _path_from_user_text(path_text: str) -> Path:
    cleaned = path_text.strip().strip('"').strip("'")
    return Path(cleaned).expanduser()


def _validate_source_file(source: Path) -> FileManagerResult | None:
    if not source.exists():
        return FileManagerResult(f"File not found: {source}", False)
    if not source.is_file():
        return FileManagerResult("Source must be a file. Folders are not supported yet.", False)

    return None


def _move_file_to_folder(source: Path, destination_folder: Path) -> FileManagerResult:
    destination_folder.mkdir(parents=True, exist_ok=True)
    target = _safe_destination(destination_folder, source.name)
    try:
        shutil.move(str(source), str(target))
    except OSError as error:
        return FileManagerResult(f"I could not move that file: {error}", False)

    return FileManagerResult(f"File moved to: {target}", True, str(target))


def _record_trash_metadata(original_path: Path, trash_path: str) -> None:
    TrashManager(TRASH_ROOT).record_trashed_file(str(original_path), trash_path)


def _new_trash_folder() -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    trash_folder = TRASH_ROOT / timestamp
    trash_folder.mkdir(parents=True, exist_ok=True)
    return trash_folder


def _safe_destination(folder: Path, filename: str) -> Path:
    candidate = folder / filename
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    for index in count(1):
        new_candidate = folder / f"{stem}_{index}{suffix}"
        if not new_candidate.exists():
            return new_candidate

    raise RuntimeError("Could not create a safe destination filename.")


def _format_paths(title: str, paths: list[Path]) -> str:
    lines = [title]
    lines.extend(f"- {path}" for path in paths)
    return "\n".join(lines)
