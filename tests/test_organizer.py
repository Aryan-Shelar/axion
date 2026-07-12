"""Tests for Axion's Smart Laptop Organizer."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from axion.tools.organizer import SmartOrganizer, classify_file


class SmartOrganizerTests(unittest.TestCase):
    def test_file_classification(self) -> None:
        cases = {
            "screenshot_test.png": "screenshots",
            "photo.jpg": "images",
            "movie.mp4": "videos",
            "test.pdf": "pdfs",
            "notes.txt": "documents",
            "budget.csv": "spreadsheets",
            "slides.pptx": "presentations",
            "archive.zip": "archives",
            "code_test.py": "code",
            "app_setup.exe": "installers",
            "certificate_school.pdf": "certificates",
            "resume_aryan.pdf": "resumes",
            "invoice_test.pdf": "receipts",
            "random.xyz": "unknown",
        }

        for filename, expected_category in cases.items():
            with self.subTest(filename=filename):
                category, _reason = classify_file(Path(filename))
                self.assertEqual(category, expected_category)

    def test_scan_saves_suggestions_and_preview_groups_them(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            home = root / "home"
            target = home / "Downloads" / "axion_organizer_test"
            target.mkdir(parents=True)
            state_path = root / "organizer_state.json"
            for filename in [
                "test.pdf",
                "screenshot_test.png",
                "resume_aryan.pdf",
                "invoice_test.pdf",
                "app_setup.exe",
                "code_test.py",
                "random.xyz",
            ]:
                (target / filename).write_text("test", encoding="utf-8")

            organizer = SmartOrganizer(state_path=state_path, home=home)
            scan_result = organizer.scan(str(target))
            preview_result = organizer.preview()

        self.assertTrue(scan_result.success)
        self.assertEqual(scan_result.count, 7)
        self.assertTrue(preview_result.success)
        self.assertIn("Organizer Preview", preview_result.message)
        self.assertIn("pdfs:", preview_result.message)
        self.assertIn("screenshots:", preview_result.message)
        self.assertIn("resume_aryan.pdf", preview_result.message)

    def test_apply_requires_confirmation(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            home = root / "home"
            target = home / "Downloads" / "axion_organizer_test"
            target.mkdir(parents=True)
            source = target / "test.pdf"
            source.write_text("test", encoding="utf-8")

            organizer = SmartOrganizer(
                state_path=root / "organizer_state.json",
                home=home,
            )
            organizer.scan(str(target))
            organizer.preview()
            result = organizer.apply(confirm=False)

            self.assertFalse(result.success)
            self.assertTrue(source.exists())
            self.assertFalse((home / "Documents" / "PDFs" / "test.pdf").exists())

    def test_apply_uses_safe_name_when_destination_exists(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            home = root / "home"
            target = home / "Downloads" / "axion_organizer_test"
            destination_folder = home / "Documents" / "PDFs"
            target.mkdir(parents=True)
            destination_folder.mkdir(parents=True)
            source = target / "test.pdf"
            source.write_text("new", encoding="utf-8")
            existing = destination_folder / "test.pdf"
            existing.write_text("existing", encoding="utf-8")

            organizer = SmartOrganizer(
                state_path=root / "organizer_state.json",
                home=home,
            )
            organizer.scan(str(target))
            organizer.preview()
            result = organizer.apply(confirm=True)

            safe_target = destination_folder / "test_1.pdf"
            self.assertTrue(result.success)
            self.assertFalse(source.exists())
            self.assertEqual(existing.read_text(encoding="utf-8"), "existing")
            self.assertEqual(safe_target.read_text(encoding="utf-8"), "new")

    def test_undo_latest_session_restores_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            home = root / "home"
            target = home / "Downloads" / "axion_organizer_test"
            target.mkdir(parents=True)
            source = target / "undo.pdf"
            source.write_text("restore me", encoding="utf-8")
            destination = home / "Documents" / "PDFs" / "undo.pdf"

            organizer = SmartOrganizer(
                state_path=root / "organizer_state.json",
                home=home,
            )
            organizer.scan(str(target))
            organizer.preview()
            apply_result = organizer.apply(confirm=True)
            undo_result = organizer.undo_last()
            second_undo = organizer.undo_last()

            self.assertTrue(apply_result.success)
            self.assertTrue(undo_result.success)
            self.assertTrue(source.exists())
            self.assertFalse(destination.exists())
            self.assertFalse(second_undo.success)


if __name__ == "__main__":
    unittest.main()
