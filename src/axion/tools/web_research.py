"""Browser Research Lite helpers for Axion.

v0.9 only opens useful browser searches and safe URLs. It does not scrape
websites, fill forms, click pages, or automate browsing sessions.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus, urlparse
import webbrowser


GOOGLE_SEARCH_URL = "https://www.google.com/search?q={query}"
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={query}"
GITHUB_SEARCH_URL = "https://github.com/search?q={query}"


@dataclass(frozen=True)
class WebResearchResult:
    """A browser research action result."""

    message: str
    success: bool
    url: str = ""


def open_google_search(query: str) -> WebResearchResult:
    """Open a Google search for the given query."""
    query = query.strip()
    if not query:
        return WebResearchResult("Usage: /web search <query>", False)

    url = GOOGLE_SEARCH_URL.format(query=quote_plus(query))
    return _open_url(url, f"Opened Google search for: {query}")


def open_youtube_search(query: str) -> WebResearchResult:
    """Open a YouTube search for the given query."""
    query = query.strip()
    if not query:
        return WebResearchResult("Usage: /web youtube <query>", False)

    url = YOUTUBE_SEARCH_URL.format(query=quote_plus(query))
    return _open_url(url, f"Opened YouTube search for: {query}")


def open_github_search(query: str) -> WebResearchResult:
    """Open a GitHub search for the given query."""
    query = query.strip()
    if not query:
        return WebResearchResult("Usage: /web github <query>", False)

    url = GITHUB_SEARCH_URL.format(query=quote_plus(query))
    return _open_url(url, f"Opened GitHub search for: {query}")


def open_web_url(url_text: str) -> WebResearchResult:
    """Open a safe http or https URL."""
    url_text = url_text.strip()
    if not url_text:
        return WebResearchResult("Usage: /web open <url>", False)

    url = _normalize_url(url_text)
    if url is None:
        return WebResearchResult("Only http and https URLs are supported.", False)

    return _open_url(url, f"Opened URL: {url}")


def _normalize_url(url_text: str) -> str | None:
    parsed = urlparse(url_text)
    if not parsed.scheme:
        url_text = f"https://{url_text}"
        parsed = urlparse(url_text)

    if parsed.scheme.lower() not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None

    return url_text


def _open_url(url: str, success_message: str) -> WebResearchResult:
    try:
        opened = webbrowser.open(url)
    except Exception as error:
        return WebResearchResult(f"Could not open browser: {error}", False, url)

    if not opened:
        return WebResearchResult("Could not open browser.", False, url)

    return WebResearchResult(success_message, True, url)
