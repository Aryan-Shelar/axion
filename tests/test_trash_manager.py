"""Tests for Axion Trash Manager."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from axion.tools.trash_manager import TrashManager


class TrashManagerTests(unittest.TestCase):
    def test_record_list_and_show_trash_item(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            trash_root = root / "trash"
            trashed_file = trash_root / "2026-07-10_120000" / "note.txt"
            trashed_file.parent.mkdir(parents=True)
            trashed_file.write_text("hello", encoding="utf-8")
            manager = TrashManager(trash_root)

            trash_id = manager.record_trashed_file(
                str(root / "Downloads" / "note.txt"),
                str(trashed_file),
            )
            listing = manager.list_trash()
            detail = manager.show_item(trash_id)

        self.assertTrue(listing.success)
        self.assertIn("note.txt", listing.message)
        self.assertIn("[trashed]", listing.message)
        self.assertTrue(detail.success)
        self.assertIn("Original path:", detail.message)
        self.assertIn("Trash path:", detail.message)

    def test_orphan_files_are_listed(self) -> None:
        with TemporaryDirectory() as temp_dir:
            trash_root = Path(temp_dir) / "trash"
            orphan = trash_root / "old" / "orphan.txt"
            orphan.parent.mkdir(parents=True)
            orphan.write_text("orphan", encoding="utf-8")
            manager = TrashManager(trash_root)

            listing = manager.list_trash()

        self.assertIn("Orphan trash files without metadata: 1", listing.message)
        self.assertIn("orphan.txt", listing.message)

    def test_restore_never_overwrites(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            trash_root = root / "trash"
            original_folder = root / "Documents"
            original_folder.mkdir()
            existing = original_folder / "restore.txt"
            existing.write_text("existing", encoding="utf-8")
            trashed_file = trash_root / "batch" / "restore.txt"
            trashed_file.parent.mkdir(parents=True)
            trashed_file.write_text("trashed", encoding="utf-8")
            manager = TrashManager(trash_root)
            trash_id = manager.record_trashed_file(
                str(original_folder / "restore.txt"),
                str(trashed_file),
            )

            result = manager.restore_item(trash_id)

            restored = original_folder / "restore_1.txt"
            self.assertTrue(result.success)
            self.assertEqual(existing.read_text(encoding="utf-8"), "existing")
            self.assertEqual(restored.read_text(encoding="utf-8"), "trashed")
            self.assertEqual(manager.show_item(trash_id).message.count("restored"), 1)

    def test_empty_trash_requires_confirm(self) -> None:
        with TemporaryDirectory() as temp_dir:
            trash_root = Path(temp_dir) / "trash"
            trashed_file = trash_root / "batch" / "delete.txt"
            trashed_file.parent.mkdir(parents=True)
            trashed_file.write_text("delete", encoding="utf-8")
            manager = TrashManager(trash_root)
            manager.record_trashed_file("C:/old/delete.txt", str(trashed_file))

            blocked = manager.empty_trash(confirm=False)
            exists_after_blocked = trashed_file.exists()
            preview = manager.empty_preview()
            emptied = manager.empty_trash(confirm=True)
            exists_after_empty = trashed_file.exists()
            detail = manager.show_item(1).message

            self.assertFalse(blocked.success)
            self.assertTrue(exists_after_blocked)
            self.assertIn("1 file(s)", preview.message)
            self.assertTrue(emptied.success)
            self.assertFalse(exists_after_empty)
            self.assertIn("deleted", detail)


if __name__ == "__main__":
    unittest.main()
