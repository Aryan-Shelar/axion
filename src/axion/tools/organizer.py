"""Smart Laptop Organizer for safe folder cleanup.

The organizer is preview-first: scans only suggest moves, apply requires
``--confirm``, and the latest apply session can be undone.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from itertools import count
import json
from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STATE_PATH = PROJECT_ROOT / "data" / "organizer" / "organizer_state.json"

SKIPPED_FOLDER_NAMES = {
    ".git",
    ".pnpm-store",
    ".venv",
    "__pycache__",
    "env",
    "node_modules",
    "site-packages",
}

SYSTEM_FOLDER_NAMES = {
    "$recycle.bin",
    "appdata",
    "program files",
    "program files (x86)",
    "programdata",
    "windows",
}

SCREENSHOT_KEYWORDS = (
    "screenshot",
    "screen shot",
    "screencapture",
    "snip",
    "whatsapp image",
    "img_",
)
CERTIFICATE_KEYWORDS = (
    "certificate",
    "cert",
    "marksheet",
    "result",
    "aadhaar",
    "pan",
    "caste",
    "validity",
    "bonafide",
)
RESUME_KEYWORDS = ("resume", "cv", "biodata")
RECEIPT_KEYWORDS = ("receipt", "invoice", "bill", "payment")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}
SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
PDF_EXTENSIONS = {".pdf"}
DOCUMENT_EXTENSIONS = {".doc", ".docx", ".txt", ".rtf"}
SPREADSHEET_EXTENSIONS = {".xls", ".xlsx", ".csv"}
PRESENTATION_EXTENSIONS = {".ppt", ".pptx"}
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".tar", ".gz"}
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".json",
    ".md",
    ".java",
    ".cpp",
    ".c",
    ".cs",
}
INSTALLER_EXTENSIONS = {".exe", ".msi"}


@dataclass(frozen=True)
class OrganizerResult:
    """A user-facing organizer result."""

    message: str
    success: bool = True
    count: int = 0


def classify_file(path: Path) -> tuple[str, str]:
    """Classify a file path into an organizer category and reason."""
    filename = path.name.lower()
    extension = path.suffix.lower()

    if extension in SCREENSHOT_EXTENSIONS and _contains_any(filename, SCREENSHOT_KEYWORDS):
        return "screenshots", "screenshot-like image filename"
    if _contains_any(filename, CERTIFICATE_KEYWORDS):
        return "certificates", "important certificate-like filename"
    if _contains_any(filename, RESUME_KEYWORDS):
        return "resumes", "resume-like filename"
    if _contains_any(filename, RECEIPT_KEYWORDS):
        return "receipts", "receipt or invoice-like filename"
    if extension in IMAGE_EXTENSIONS:
        return "images", "image extension"
    if extension in VIDEO_EXTENSIONS:
        return "videos", "video extension"
    if extension in PDF_EXTENSIONS:
        return "pdfs", "PDF extension"
    if extension in DOCUMENT_EXTENSIONS:
        return "documents", "document extension"
    if extension in SPREADSHEET_EXTENSIONS:
        return "spreadsheets", "spreadsheet extension"
    if extension in PRESENTATION_EXTENSIONS:
        return "presentations", "presentation extension"
    if extension in ARCHIVE_EXTENSIONS:
        return "archives", "archive extension"
    if extension in CODE_EXTENSIONS:
        return "code", "code file extension"
    if extension in INSTALLER_EXTENSIONS:
        return "installers", "installer extension"

    return "unknown", "unknown file type"


class SmartOrganizer:
    """Scan, preview, apply, and undo safe organization moves."""

    def __init__(self, state_path: Path | None = None, home: Path | None = None) -> None:
        self.state_path = state_path or STATE_PATH
        self.home = home or Path.home()

    def scan(self, target_text: str) -> OrganizerResult:
        """Scan one folder shallowly and save pending suggestions."""
        target_result = self._resolve_target_folder(target_text)
        if not target_result.success:
            return target_result

        target = Path(target_result.message)
        suggestions = []
        skipped_count = 0
        scanned_count = 0

        try:
            children = sorted(target.iterdir(), key=lambda path: path.name.lower())
        except OSError as error:
            return OrganizerResult(f"Could not scan folder: {error}", success=False)

        for child in children:
            if child.is_dir() or not child.is_file() or child.name.startswith("."):
                skipped_count += 1
                continue

            scanned_count += 1
            category, reason = classify_file(child)
            destination_folder = self._destination_folder(category)
            destination_path = destination_folder / child.name
            if _same_path(child, destination_path):
                skipped_count += 1
                continue

            suggestions.append(
                {
                    "id": len(suggestions) + 1,
                    "source_path": str(child),
                    "destination_path": str(destination_path),
                    "filename": child.name,
                    "category": category,
                    "reason": reason,
                    "status": "pending",
                }
            )

        timestamp = self._timestamp()
        state = self._load_state()
        state["latest_scan"] = {
            "target_folder": str(target),
            "created_at": timestamp,
            "suggested_moves": suggestions,
            "previewed": False,
        }
        state["target_folder"] = str(target)
        state["created_at"] = timestamp
        state["suggested_moves"] = suggestions
        self._save_state(state)

        categories = sorted({item["category"] for item in suggestions})
        category_text = ", ".join(categories) if categories else "(none)"
        return OrganizerResult(
            "\n".join(
                [
                    "Organizer scan complete.",
                    f"Target folder: {target}",
                    f"Scanned files: {scanned_count}",
                    f"Suggested moves: {len(suggestions)}",
                    f"Skipped files: {skipped_count}",
                    f"Categories found: {category_text}",
                    "Run /organize preview to review suggestions.",
                ]
            ),
            count=len(suggestions),
        )

    def preview(self) -> OrganizerResult:
        """Show latest scan suggestions and mark them previewed."""
        state = self._load_state()
        latest_scan = state.get("latest_scan") or {}
        suggestions = latest_scan.get("suggested_moves") or []
        if not latest_scan:
            return OrganizerResult(
                "No organizer scan found. Run /organize scan <folder> first.",
                success=False,
            )
        if not suggestions:
            return OrganizerResult("No pending organizer suggestions to preview.")

        latest_scan["previewed"] = True
        state["latest_scan"] = latest_scan
        self._save_state(state)

        lines = [
            "Organizer Preview",
            f"Target folder: {latest_scan.get('target_folder')}",
        ]
        for category in self._ordered_categories(suggestions):
            lines.append("")
            lines.append(f"{category}:")
            for item in suggestions:
                if item["category"] != category:
                    continue
                destination_folder = Path(item["destination_path"]).parent
                lines.append(
                    f"{item['id']}. {item['filename']} -> {destination_folder}"
                )

        lines.append("")
        lines.append("Run /organize apply --confirm to move these files.")
        return OrganizerResult("\n".join(lines), count=len(suggestions))

    def apply(self, confirm: bool = False) -> OrganizerResult:
        """Apply latest pending suggestions after confirmation."""
        if not confirm:
            return OrganizerResult(
                "Preview first with /organize preview. To apply, run /organize apply --confirm.",
                success=False,
            )

        state = self._load_state()
        latest_scan = state.get("latest_scan") or {}
        if not latest_scan:
            return OrganizerResult(
                "No organizer scan found. Run /organize scan <folder> first.",
                success=False,
            )
        if not latest_scan.get("previewed"):
            return OrganizerResult(
                "Preview first with /organize preview. To apply, run /organize apply --confirm.",
                success=False,
            )

        suggestions = latest_scan.get("suggested_moves") or []
        pending = [item for item in suggestions if item.get("status") == "pending"]
        if not pending:
            return OrganizerResult("No pending organizer suggestions to apply.")

        session_id = self._session_id()
        moved_count = 0
        skipped_count = 0
        failed_count = 0
        moves = []

        for item in pending:
            source = Path(item["source_path"])
            destination = Path(item["destination_path"])
            move_record = dict(item)

            if not source.exists() or not source.is_file():
                item["status"] = "failed"
                move_record["status"] = "failed"
                move_record["error"] = "Source file is missing."
                failed_count += 1
                moves.append(move_record)
                continue

            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                final_destination = self._safe_destination(destination.parent, destination.name)
                if _same_path(source, final_destination):
                    item["status"] = "skipped"
                    move_record["status"] = "skipped"
                    move_record["error"] = "Source is already at destination."
                    skipped_count += 1
                    moves.append(move_record)
                    continue

                shutil.move(str(source), str(final_destination))
            except OSError as error:
                item["status"] = "failed"
                move_record["status"] = "failed"
                move_record["error"] = str(error)
                failed_count += 1
                moves.append(move_record)
                continue

            item["status"] = "moved"
            item["destination_path"] = str(final_destination)
            move_record["status"] = "moved"
            move_record["destination_path"] = str(final_destination)
            moved_count += 1
            moves.append(move_record)

        session_status = "applied" if failed_count == 0 else "partial"
        session = {
            "session_id": session_id,
            "applied_at": self._timestamp(),
            "moves": moves,
            "status": session_status,
        }
        state["latest_scan"] = latest_scan
        state["suggested_moves"] = suggestions
        state.setdefault("move_sessions", []).append(session)
        state["latest_session_id"] = session_id
        self._save_state(state)

        return OrganizerResult(
            "\n".join(
                [
                    "Organizer apply complete.",
                    f"Moved: {moved_count}",
                    f"Skipped: {skipped_count}",
                    f"Failed: {failed_count}",
                    "Run /organize undo-last to reverse the latest move session.",
                ]
            ),
            success=failed_count == 0,
            count=moved_count,
        )

    def undo_last(self) -> OrganizerResult:
        """Undo the latest organizer apply session only."""
        state = self._load_state()
        session = self._latest_session(state)
        if session is None or session.get("status") in {"undone", "empty"}:
            return OrganizerResult("No organizer move session is available to undo.", success=False)

        undone_count = 0
        skipped_count = 0
        failed_count = 0
        moves = session.get("moves") or []
        suggestions = (state.get("latest_scan") or {}).get("suggested_moves") or []

        for move in reversed(moves):
            if move.get("status") != "moved":
                skipped_count += 1
                continue

            current_path = Path(move["destination_path"])
            original_path = Path(move["source_path"])

            if not current_path.exists() or not current_path.is_file():
                move["status"] = "failed"
                move["error"] = "Moved file is missing."
                failed_count += 1
                continue
            if original_path.exists():
                move["status"] = "skipped"
                move["error"] = "Original path already exists."
                skipped_count += 1
                continue
            if not original_path.parent.exists():
                move["status"] = "failed"
                move["error"] = "Original folder no longer exists."
                failed_count += 1
                continue

            try:
                shutil.move(str(current_path), str(original_path))
            except OSError as error:
                move["status"] = "failed"
                move["error"] = str(error)
                failed_count += 1
                continue

            move["status"] = "undone"
            undone_count += 1
            self._mark_suggestion_status(suggestions, int(move["id"]), "undone")

        if failed_count == 0 and skipped_count == 0:
            session["status"] = "undone"
        else:
            session["status"] = "partial_undo"

        self._save_state(state)
        return OrganizerResult(
            "\n".join(
                [
                    "Organizer undo complete.",
                    f"Undone: {undone_count}",
                    f"Skipped: {skipped_count}",
                    f"Failed: {failed_count}",
                ]
            ),
            success=failed_count == 0,
            count=undone_count,
        )

    def status(self) -> OrganizerResult:
        """Return current organizer status."""
        state = self._load_state()
        latest_scan = state.get("latest_scan") or {}
        latest_session = self._latest_session(state)
        suggestion_count = len(latest_scan.get("suggested_moves") or [])
        latest_session_text = (
            f"{latest_session.get('session_id')} [{latest_session.get('status')}]"
            if latest_session
            else "(none)"
        )
        undo_available = self._undo_available(state)

        return OrganizerResult(
            "\n".join(
                [
                    "Smart Organizer status:",
                    f"Latest scan folder: {latest_scan.get('target_folder') or '(none)'}",
                    f"Suggested moves: {suggestion_count}",
                    f"Latest move session: {latest_session_text}",
                    f"Undo available: {'yes' if undo_available else 'no'}",
                ]
            )
        )

    def clear(self) -> OrganizerResult:
        """Clear latest scan suggestions without deleting move history."""
        state = self._load_state()
        state["latest_scan"] = None
        state["target_folder"] = None
        state["created_at"] = None
        state["suggested_moves"] = []
        self._save_state(state)
        return OrganizerResult(
            "Organizer scan suggestions cleared. Move history was preserved."
        )

    def latest_scan_count(self) -> int:
        """Return the latest scan suggestion count for status output."""
        latest_scan = self._load_state().get("latest_scan") or {}
        return len(latest_scan.get("suggested_moves") or [])

    def latest_session_label(self) -> str:
        """Return the latest move session label for status output."""
        session = self._latest_session(self._load_state())
        if not session:
            return "(none)"

        return f"{session.get('session_id')} [{session.get('status')}]"

    def _resolve_target_folder(self, target_text: str) -> OrganizerResult:
        target_text = target_text.strip()
        if not target_text:
            return OrganizerResult("Usage: /organize scan <folder>", success=False)

        shortcuts = {
            "desktop": self.home / "Desktop",
            "documents": self.home / "Documents",
            "downloads": self.home / "Downloads",
            "pictures": self.home / "Pictures",
        }
        target = shortcuts.get(target_text.lower())
        if target is None:
            target = self._path_from_user_text(target_text)

        if not target.exists():
            return OrganizerResult(f"Folder not found: {target}", success=False)
        if not target.is_dir():
            return OrganizerResult(f"This path is not a folder: {target}", success=False)
        if self._is_skipped_folder(target):
            return OrganizerResult(f"Organizer skips this folder for safety: {target}", success=False)

        return OrganizerResult(str(target.resolve()))

    def _destination_folder(self, category: str) -> Path:
        documents = self.home / "Documents"
        downloads = self.home / "Downloads"
        pictures = self.home / "Pictures"
        videos = self.home / "Videos"
        mapping = {
            "screenshots": pictures / "Screenshots",
            "images": pictures / "Images",
            "videos": videos / "Organized",
            "pdfs": documents / "PDFs",
            "documents": documents / "Docs",
            "spreadsheets": documents / "Spreadsheets",
            "presentations": documents / "Presentations",
            "archives": downloads / "Archives",
            "code": documents / "Code Files",
            "installers": downloads / "Installers",
            "certificates": documents / "Certificates",
            "resumes": documents / "Resume",
            "receipts": documents / "Receipts",
            "unknown": downloads / "Unsorted",
        }
        return mapping[category]

    def _ordered_categories(self, suggestions: list[dict]) -> list[str]:
        order = [
            "screenshots",
            "images",
            "videos",
            "pdfs",
            "documents",
            "spreadsheets",
            "presentations",
            "archives",
            "code",
            "installers",
            "certificates",
            "resumes",
            "receipts",
            "unknown",
        ]
        present = {item["category"] for item in suggestions}
        return [category for category in order if category in present]

    def _load_state(self) -> dict:
        default = self._default_state()
        if not self.state_path.exists():
            return default

        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return default
        if not isinstance(data, dict):
            return default

        for key, value in default.items():
            data.setdefault(key, value)
        return data

    def _save_state(self, state: dict) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def _default_state(self) -> dict:
        return {
            "latest_scan": None,
            "target_folder": None,
            "created_at": None,
            "suggested_moves": [],
            "move_sessions": [],
            "latest_session_id": None,
        }

    def _latest_session(self, state: dict) -> dict | None:
        latest_session_id = state.get("latest_session_id")
        sessions = state.get("move_sessions") or []
        if not latest_session_id and sessions:
            return sessions[-1]

        for session in sessions:
            if session.get("session_id") == latest_session_id:
                return session
        return None

    def _undo_available(self, state: dict) -> bool:
        session = self._latest_session(state)
        if not session or session.get("status") in {"undone", "empty"}:
            return False

        return any(move.get("status") == "moved" for move in session.get("moves") or [])

    def _mark_suggestion_status(
        self,
        suggestions: list[dict],
        suggestion_id: int,
        status: str,
    ) -> None:
        for item in suggestions:
            if int(item.get("id", 0)) == suggestion_id:
                item["status"] = status
                return

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

    def _is_skipped_folder(self, folder: Path) -> bool:
        parts = {part.lower() for part in folder.parts}
        if parts.intersection(SKIPPED_FOLDER_NAMES | SYSTEM_FOLDER_NAMES):
            return True

        return folder.name.startswith(".")

    def _path_from_user_text(self, path_text: str) -> Path:
        cleaned = path_text.strip().strip('"').strip("'")
        return Path(cleaned).expanduser()

    def _session_id(self) -> str:
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def _timestamp(self) -> str:
        return datetime.now().isoformat(timespec="seconds")


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _same_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return False
