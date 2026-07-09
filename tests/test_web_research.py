"""Tests for Browser Research Lite."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from axion.tools.web_research import (
    open_github_search,
    open_google_search,
    open_web_url,
    open_youtube_search,
)


class WebResearchTests(unittest.TestCase):
    @patch("axion.tools.web_research.webbrowser.open")
    def test_google_search_opens_encoded_query(self, mock_open) -> None:
        mock_open.return_value = True

        result = open_google_search("AI automation tools")

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Opened Google search for: AI automation tools")
        self.assertEqual(
            result.url,
            "https://www.google.com/search?q=AI+automation+tools",
        )
        mock_open.assert_called_once_with(result.url)

    @patch("axion.tools.web_research.webbrowser.open")
    def test_youtube_search_opens_encoded_query(self, mock_open) -> None:
        mock_open.return_value = True

        result = open_youtube_search("Python beginner tutorial")

        self.assertTrue(result.success)
        self.assertEqual(
            result.url,
            "https://www.youtube.com/results?search_query=Python+beginner+tutorial",
        )
        mock_open.assert_called_once_with(result.url)

    @patch("axion.tools.web_research.webbrowser.open")
    def test_github_search_opens_encoded_query(self, mock_open) -> None:
        mock_open.return_value = True

        result = open_github_search("ollama python")

        self.assertTrue(result.success)
        self.assertEqual(result.url, "https://github.com/search?q=ollama+python")
        mock_open.assert_called_once_with(result.url)

    @patch("axion.tools.web_research.webbrowser.open")
    def test_open_url_adds_https_when_missing(self, mock_open) -> None:
        mock_open.return_value = True

        result = open_web_url("github.com")

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Opened URL: https://github.com")
        self.assertEqual(result.url, "https://github.com")
        mock_open.assert_called_once_with("https://github.com")

    @patch("axion.tools.web_research.webbrowser.open")
    def test_open_url_rejects_unsafe_scheme(self, mock_open) -> None:
        result = open_web_url("file:///C:/Users/ADMIN/secrets.txt")

        self.assertFalse(result.success)
        self.assertEqual(result.message, "Only http and https URLs are supported.")
        mock_open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
