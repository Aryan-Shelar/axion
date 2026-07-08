"""Open websites from Axion commands."""

from __future__ import annotations

import webbrowser
from urllib.parse import urlparse


def open_url(url_text: str) -> str:
    """Validate, normalize, and open a URL."""
    cleaned_url = url_text.strip()

    if not cleaned_url:
        return "Usage: /open <url>"

    url = normalize_url(cleaned_url)
    opened = webbrowser.open(url)

    if not opened:
        return f"I could not open {url}."

    return f"Opened {url}"


def normalize_url(value: str) -> str:
    """Add https:// when the user provides a bare domain."""
    parsed = urlparse(value)
    if parsed.scheme:
        return value

    return f"https://{value}"
