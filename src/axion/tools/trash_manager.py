"""Trash Manager and restore support for Axion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from itertools import count
import json
from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRASH_ROOT = PROJECT_ROOT / "data" / "trash"
TRASH_INDEX_NAME = "trash_index.json"


@dataclass(frozen=True)
class TrashResult:
    """A user-facing Trash Manager result."""

    message: str
    success: bool = True
    count: int = 0


class TrashManager:
    """Track, inspect, restore, and empty files in Axion Trash."""

    def __init__(self, trash_root: Path | None = None) -> None:
        self.trash_root = trash_root or TRASH_ROOT
        self.index_path = self.trash_root / TRASH_INDEX_NAME

    def record_trashed_file(self, original_path: str, trash_path: str) -> int:
        """Record a newly trashed file and return its trash id."""
        self.trash_root.mkdir(parents=True, exist_ok=True)
        records = self._load_records()
        trash_id = self._next_id(records)
        timestamp = self._timestamp()
        records.append(
            {
                "id": trash_id,
                "original_path": str(Path(original_path)),
                "trash_path": str(Path(trash_path)),
                "filename": Path(trash_path).name,
                "trashed_at": timestamp,
                "restored_at": None,
                "status": "trashed",
            }
        )
        self._save_records(records)
        return trash_id

    def list_trash(self) -> TrashResult:
        """List tracked trash records and orphan files."""
        records = self._load_records()
        orphans = self._orphan_files(records)
        if not records and not orphans:
            return TrashResult("Axion Trash is empty.")

        lines = ["Axion Trash:"]
        if records:
            for record in records:
                lines.append(
                    f"{record['id']}. {record['filename']} "
                    f"[{record['status']}] trashed={record.get('trashed_at') or '(unknown)'}"
                )
        else:
            lines.append("No tracked trash records.")

        if orphans:
            lines.append("")
            lines.append(f"Orphan trash files without metadata: {len(orphans)}")
            for orphan in orphans:
                lines.append(f"- {orphan}")

        return TrashResult("\n".join(lines), count=len(records))

    def show_item(self, trash_id: int) -> TrashResult:
        """Show one tracked trash record."""
        record = self._find_record(trash_id)
        if record is None:
            return TrashResult(f"Trash item {trash_id} was not found.", success=False)

        return TrashResult(
            "\n".join(
                [
                    f"Trash item {record['id']}:",
                    f"Filename: {record['filename']}",
                    f"Original path: {record['original_path']}",
                    f"Trash path: {record['trash_path']}",
                    f"Status: {record['status']}",
                    f"Trashed at: {record.get('trashed_at') or '(unknown)'}",
                    f"Restored at: {record.get('restored_at') or '(not restored)'}",
                ]
            )
        )

    def restore_item(
        self,
        trash_id: int,
        destination_folder: str | None = None,
    ) -> TrashResult:
        """Restore one tracked trash item without overwriting."""
        records = self._load_records()
        record = self._find_record(trash_id, records)
        if record is None:
            return TrashResult(f"Trash item {trash_id} was not found.", success=False)
        if record.get("status") != "trashed":
            return TrashResult(
                f"Trash item {trash_id} is not currently trashed.",
                success=False,
            )

        source = Path(record["trash_path"])
        if not self._is_inside_trash(source) or not source.exists() or not source.is_file():
            return TrashResult(
                f"Trash file is missing or unsafe to restore: {source}",
                success=False,
            )

        if destination_folder:
            destination = self._path_from_user_text(destination_folder)
            if not destination.exists():
                return TrashResult(
                    f"Destination folder not found: {destination}",
                    success=False,
                )
            if not destination.is_dir():
                return TrashResult("Destination must be a folder.", success=False)
        else:
            destination = Path(record["original_path"]).expanduser().parent
            if not destination.exists():
                return TrashResult(
                    (
                        "Original folder does not exist. "
                        f"To restore elsewhere, run: /restore {trash_id} :: <destination_folder>"
                    ),
                    success=False,
                )

        target = self._safe_destination(destination, record["filename"])
        try:
            shutil.move(str(source), str(target))
        except OSError as error:
            return TrashResult(f"Could not restore file: {error}", success=False)

        record["status"] = "restored"
        record["restored_at"] = self._timestamp()
        self._save_records(records)
        return TrashResult(f"Restored file to: {target}", count=1)

    def empty_preview(self) -> TrashResult:
        """Preview what emptying trash would permanently delete."""
        files = self._empty_candidates()
        total_size = self._total_size(files)
        return TrashResult(
            (
                f"Empty trash preview: {len(files)} file(s) would be permanently "
                f"deleted from Axion Trash. Total size: {total_size} bytes."
            ),
            count=len(files),
        )

    def empty_trash(self, confirm: bool = False) -> TrashResult:
        """Permanently delete trash files only after explicit confirmation."""
        if not confirm:
            return TrashResult(
                "Preview first with /empty-trash preview. To empty, run /empty-trash --confirm.",
                success=False,
            )

        records = self._load_records()
        files = self._empty_candidates(records)
        deleted_count = 0
        deleted_paths = {str(path.resolve()) for path in files}

        for path in files:
            if not self._is_inside_trash(path) or not path.is_file():
                continue
            try:
                path.unlink()
                deleted_count += 1
            except OSError:
                continue

        for record in records:
            trash_path = Path(record.get("trash_path", ""))
            if (
                record.get("status") == "trashed"
                and trash_path.exists() is False
                and str(trash_path.resolve()) in deleted_paths
            ):
                record["status"] = "deleted"

        self._save_records(records)
        return TrashResult(
            f"Emptied Axion Trash. Permanently deleted {deleted_count} file(s).",
            count=deleted_count,
        )

    def count_trashed(self) -> int:
        """Return current trashed count, including orphan files."""
        records = self._load_records()
        tracked_count = sum(1 for record in records if record.get("status") == "trashed")
        return tracked_count + len(self._orphan_files(records))

    def count_restored(self) -> int:
        """Return restored metadata count."""
        return sum(1 for record in self._load_records() if record.get("status") == "restored")

    def _empty_candidates(self, records: list[dict] | None = None) -> list[Path]:
        records = records if records is not None else self._load_records()
        files: list[Path] = []
        for record in records:
            path = Path(record.get("trash_path", ""))
            if record.get("status") == "trashed" and self._is_inside_trash(path) and path.is_file():
                files.append(path)

        files.extend(self._orphan_files(records))
        return files

    def _orphan_files(self, records: list[dict]) -> list[Path]:
        self.trash_root.mkdir(parents=True, exist_ok=True)
        known_paths = {
            str(Path(record.get("trash_path", "")).resolve())
            for record in records
            if record.get("trash_path")
        }
        orphans = []
        for path in self.trash_root.rglob("*"):
            if path == self.index_path or not path.is_file():
                continue
            if not self._is_inside_trash(path):
                continue
            if str(path.resolve()) not in known_paths:
                orphans.append(path)

        return sorted(orphans)

    def _find_record(self, trash_id: int, records: list[dict] | None = None) -> dict | None:
        records = records if records is not None else self._load_records()
        for record in records:
            if int(record.get("id", 0)) == trash_id:
                return record

        return None

    def _load_records(self) -> list[dict]:
        if not self.index_path.exists():
            return []

        try:
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(data, list):
            return []

        return [record for record in data if isinstance(record, dict)]

    def _save_records(self, records: list[dict]) -> None:
        self.trash_root.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(
            json.dumps(records, indent=2),
            encoding="utf-8",
        )

    def _is_inside_trash(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.trash_root.resolve())
            return True
        except (OSError, ValueError):
            return False

    def _safe_destination(self, folder: Path, filename: str) -> Path:
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

    def _total_size(self, files: list[Path]) -> int:
        total = 0
        for path in files:
            try:
                total += path.stat().st_size
            except OSError:
                continue

        return total

    def _next_id(self, records: list[dict]) -> int:
        if not records:
            return 1

        return max(int(record.get("id", 0)) for record in records) + 1

    def _path_from_user_text(self, path_text: str) -> Path:
        cleaned = path_text.strip().strip('"').strip("'")
        return Path(cleaned).expanduser()

    def _timestamp(self) -> str:
        return datetime.now().isoformat(timespec="seconds")
