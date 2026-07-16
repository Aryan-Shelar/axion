"""Safe, persisted filename search and selective actions."""
from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

from axion.tools.trash_manager import TrashManager

SKIPPED = {".git", "node_modules", "__pycache__", ".venv", "env", "site-packages", ".pnpm-store"}
ALIASES = {"desktop": "Desktop", "downloads": "Downloads", "documents": "Documents", "pictures": "Pictures", "videos": "Videos"}

@dataclass
class Match:
    result_id: int
    filename: str
    path: str
    extension: str
    size: int
    modified: str
    score: float
    reason: str

class SmartFileFinder:
    def __init__(self, state_path: Path | None = None, home: Path | None = None, max_files: int = 10000, trash_manager: TrashManager | None = None):
        self.state_path = state_path or Path("data/search/search_state.json")
        self.home = home or Path.home()
        self.max_files = max_files
        self.trash_manager = trash_manager or TrashManager()

    def resolve_folder(self, value: str) -> Path:
        return self.home / ALIASES[value.lower()] if value.lower() in ALIASES else Path(value).expanduser()

    def search(self, query: str, folder: str, recursive: bool = False) -> list[Match]:
        root = self.resolve_folder(folder)
        if not root.is_dir(): raise ValueError(f"Folder does not exist: {root}")
        found = []
        iterator = root.rglob("*") if recursive else root.iterdir()
        scanned = 0
        for path in iterator:
            if recursive and any(p.startswith(".") or p.lower() in SKIPPED for p in path.relative_to(root).parts[:-1]): continue
            if not path.is_file(): continue
            scanned += 1
            if scanned > self.max_files: break
            score, reason = match_filename(query, path.name)
            if score:
                stat = path.stat()
                found.append(Match(0, path.name, str(path.resolve()), path.suffix, stat.st_size, datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"), score, reason))
        found.sort(key=lambda x: (-x.score, x.filename.lower()))
        for idx, item in enumerate(found, 1): item.result_id = idx
        self._save(query, str(root), recursive, found)
        return found

    def latest(self) -> list[Match]:
        try: return [Match(**x) for x in json.loads(self.state_path.read_text(encoding="utf-8")).get("results", [])]
        except (OSError, ValueError, TypeError): return []

    def get(self, result_id: int) -> Match | None:
        return next((x for x in self.latest() if x.result_id == result_id), None)

    def move(self, result_id: int, destination: str) -> str:
        item = self.get(result_id)
        if not item: return "Search result not found."
        source, folder = Path(item.path), Path(destination).expanduser()
        if not source.is_file() or not folder.is_dir(): return "Source file or destination folder is unavailable."
        target = safe_destination(folder, source.name); shutil.move(str(source), str(target)); return f"Moved to: {target}"

    def trash(self, result_id: int) -> str:
        item = self.get(result_id)
        if not item: return "Search result not found."
        source = Path(item.path)
        if not source.is_file(): return "Source file is unavailable."
        root = self.trash_manager.trash_root; root.mkdir(parents=True, exist_ok=True)
        target = safe_destination(root, source.name); shutil.move(str(source), str(target))
        self.trash_manager.record_trashed_file(str(source), str(target)); return f"Moved to Axion Trash: {target}"

    def bulk(self, query: str, folder: str, action: str, destination: str | None = None, recursive: bool = False, confirm: bool = False) -> str:
        matches = self.search(query, folder, recursive)
        preview = "\n".join(f"- {m.path}" for m in matches) or "(none)"
        if not confirm: return f"Preview: {len(matches)} matching file(s)\n{preview}\nNo files were moved. Re-run with --confirm."
        messages = [self.move(m.result_id, destination or "") if action == "move" else self.trash(m.result_id) for m in matches]
        return f"Confirmed {action}: {len(matches)} file(s).\n" + "\n".join(messages)

    def _save(self, query: str, folder: str, recursive: bool, results: list[Match]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps({"query": query, "folder": folder, "recursive": recursive, "results": [asdict(x) for x in results]}, indent=2), encoding="utf-8")

def match_filename(query: str, filename: str) -> tuple[float, str]:
    q, name = query.casefold().strip(), Path(filename).stem.casefold()
    if not q: return 0, ""
    if q == name or q == filename.casefold(): return 1.0, "exact"
    if q in name: return .95, "contains"
    tokens = q.split()
    if tokens and all(t in name for t in tokens): return .9, "all-word/token"
    if name.startswith(q): return .88, "starts-with"
    if name.endswith(q): return .86, "ends-with"
    ratio = SequenceMatcher(None, q, name).ratio()
    return (round(ratio, 3), "fuzzy") if ratio >= .58 else (0, "")

def safe_destination(folder: Path, filename: str) -> Path:
    target = folder / filename
    if not target.exists(): return target
    stem, suffix, index = Path(filename).stem, Path(filename).suffix, 1
    while (folder / f"{stem}_{index}{suffix}").exists(): index += 1
    return folder / f"{stem}_{index}{suffix}"

def format_matches(matches: list[Match]) -> str:
    if not matches: return "No matching files found."
    return "\n\n".join(f"[{m.result_id}] {m.filename}\nPath: {m.path}\nExtension: {m.extension or '(none)'} | Size: {m.size} bytes | Modified: {m.modified}\nMatch: {m.score:.3f} ({m.reason})" for m in matches)
