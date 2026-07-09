"""Tests for Axion's Safe File Manager."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from axion.tools.file_manager import (
    clean_screenshots,
    move_file,
    search_files,
    search_files_by_extension,
    trash_file,
)


class FileManagerTests(unittest.TestCase):
    def test_search_files_by_name_skips_ignored_folders(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            visible = root / "AxionPlan.txt"
            visible.write_text("visible", encoding="utf-8")
            ignored_folder = root / "node_modules"
            ignored_folder.mkdir()
            ignored = ignored_folder / "axion-hidden.txt"
            ignored.write_text("ignored", encoding="utf-8")

            result = search_files("axion", str(root))

        self.assertTrue(result.success)
        self.assertIn("AxionPlan.txt", result.message)
        self.assertNotIn("axion-hidden.txt", result.message)

    def test_search_files_by_extension(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            python_file = root / "main.py"
            python_file.write_text("print('ok')", encoding="utf-8")
            text_file = root / "notes.txt"
            text_file.write_text("notes", encoding="utf-8")

            result = search_files_by_extension("py", str(root))

        self.assertTrue(result.success)
        self.assertIn("main.py", result.message)
        self.assertNotIn("notes.txt", result.message)

    def test_move_file_does_not_overwrite_existing_destination(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_folder = root / "source"
            destination_folder = root / "destination"
            source_folder.mkdir()
            destination_folder.mkdir()
            source = source_folder / "report.txt"
            source.write_text("new", encoding="utf-8")
            existing = destination_folder / "report.txt"
            existing.write_text("existing", encoding="utf-8")

            result = move_file(str(source), str(destination_folder))

            safe_target = destination_folder / "report_1.txt"
            self.assertTrue(result.success)
            self.assertFalse(source.exists())
            self.assertEqual(existing.read_text(encoding="utf-8"), "existing")
            self.assertEqual(safe_target.read_text(encoding="utf-8"), "new")
            self.assertIn(str(safe_target), result.message)

    def test_trash_file_moves_to_axion_trash(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            trash_root = root / "trash"
            source = root / "test.png"
            source.write_text("image", encoding="utf-8")

            with patch("axion.tools.file_manager.TRASH_ROOT", trash_root):
                result = trash_file(str(source))

            trashed_files = list(trash_root.glob("*/test.png"))
            self.assertTrue(result.success)
            self.assertFalse(source.exists())
            self.assertEqual(len(trashed_files), 1)
            self.assertEqual(trashed_files[0].read_text(encoding="utf-8"), "image")

    def test_screenshot_clean_requires_confirmation(self) -> None:
        result = clean_screenshots(confirm=False)

        self.assertFalse(result.success)
        self.assertEqual(
            result.message,
            "Preview first with /screenshots preview. To clean, run /screenshots clean --confirm.",
        )


if __name__ == "__main__":
    unittest.main()
