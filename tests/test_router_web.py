"""Tests for /web command routing."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from axion.commands.router import CommandRouter
from axion.memory.sqlite_memory import SQLiteMemory
from axion.projects.project_store import ProjectStore
from axion.tasks.task_store import TaskStore
from axion.tools.web_research import WebResearchResult


class FakeAICore:
    def is_available(self) -> bool:
        return False


def make_router(db_path: Path) -> CommandRouter:
    return CommandRouter(
        memory=SQLiteMemory(db_path),
        ai_core=FakeAICore(),
        task_store=TaskStore(db_path),
        project_store=ProjectStore(db_path),
    )


class RouterWebTests(unittest.TestCase):
    @patch("axion.commands.router.log_activity")
    @patch("axion.commands.router.open_google_search")
    def test_web_search_routes_to_google_search(
        self, mock_open_google_search, mock_log_activity
    ) -> None:
        mock_open_google_search.return_value = WebResearchResult(
            "Opened Google search for: AI automation tools",
            True,
            "https://www.google.com/search?q=AI+automation+tools",
        )

        with TemporaryDirectory() as temp_dir:
            router = make_router(Path(temp_dir) / "axion.db")
            response = router.handle("/web search AI automation tools")

        self.assertEqual(response.message, "Opened Google search for: AI automation tools")
        mock_open_google_search.assert_called_once_with("AI automation tools")
        mock_log_activity.assert_any_call("command used", "/web")
        mock_log_activity.assert_any_call(
            "web search opened",
            "https://www.google.com/search?q=AI+automation+tools",
        )

    @patch("axion.commands.router.log_activity")
    @patch("axion.commands.router.open_web_url")
    def test_web_open_routes_to_url_opener(
        self, mock_open_web_url, mock_log_activity
    ) -> None:
        mock_open_web_url.return_value = WebResearchResult(
            "Opened URL: https://github.com",
            True,
            "https://github.com",
        )

        with TemporaryDirectory() as temp_dir:
            router = make_router(Path(temp_dir) / "axion.db")
            response = router.handle("/web open github.com")

        self.assertEqual(response.message, "Opened URL: https://github.com")
        mock_open_web_url.assert_called_once_with("github.com")
        mock_log_activity.assert_any_call("command used", "/web")
        mock_log_activity.assert_any_call("web url opened", "https://github.com")


if __name__ == "__main__":
    unittest.main()
