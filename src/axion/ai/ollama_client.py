"""Small standard-library client for the local Ollama HTTP API."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


DEFAULT_MODEL = "llama3.2:1b"
DEFAULT_BASE_URL = "http://localhost:11434"

OLLAMA_NOT_RUNNING_MESSAGE = "Error: Ollama is not running. Start Ollama and try again."
MODEL_NOT_FOUND_MESSAGE = "Error: Model not found. Please run: ollama pull llama3.2:1b"


class OllamaClient:
    """Talk to a local Ollama server using only the Python standard library."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        availability_timeout_seconds: int = 5,
        generate_timeout_seconds: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.availability_timeout_seconds = availability_timeout_seconds
        self.generate_timeout_seconds = generate_timeout_seconds

    def is_available(self) -> bool:
        """Return True when Ollama responds to a lightweight local request."""
        request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.availability_timeout_seconds,
            ) as response:
                return 200 <= response.status < 300
        except (urllib.error.URLError, TimeoutError):
            return False

    def generate(self, prompt: str, model: str = DEFAULT_MODEL) -> str:
        """Generate a response from Ollama's /api/generate endpoint."""
        body = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.generate_timeout_seconds,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            return self._handle_http_error(error)
        except (urllib.error.URLError, TimeoutError) as error:
            return f"Error: Ollama request failed or timed out: {error}"
        except (json.JSONDecodeError, UnicodeDecodeError):
            return "Error: Ollama returned a response I could not read."
        except Exception as error:
            return f"Error: Unexpected Ollama client error: {error}"

        response_text = str(payload.get("response", "")).strip()
        if not response_text:
            return "Error: Ollama response was empty."

        return response_text

    def _handle_http_error(self, error: urllib.error.HTTPError) -> str:
        try:
            error_payload = json.loads(error.read().decode("utf-8"))
            error_message = str(error_payload.get("error", ""))
        except (json.JSONDecodeError, UnicodeDecodeError):
            error_message = str(error)

        if error.code == 404 or "not found" in error_message.lower():
            return MODEL_NOT_FOUND_MESSAGE

        return f"Error: {error_message}"