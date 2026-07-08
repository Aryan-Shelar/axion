"""Axion AI Core powered by a local Ollama model."""

from __future__ import annotations

from axion.ai.ollama_client import DEFAULT_MODEL, OllamaClient
from axion.ai.prompts import SYSTEM_PROMPT


class AICore:
    """Build prompts and request responses from the local AI provider."""

    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    def is_available(self) -> bool:
        """Return True when the local AI provider is reachable."""
        return self.client.is_available()

    def respond(
        self,
        user_message: str,
        recent_memories: list[str] | None = None,
        model: str = DEFAULT_MODEL,
        recent_tasks: list[str] | None = None,
    ) -> str:
        """Build a prompt and return the model response."""
        prompt = self._build_prompt(user_message, recent_memories, recent_tasks)
        return self.client.generate(prompt, model=model)

    def _build_prompt(
        self,
        user_message: str,
        recent_memories: list[str] | None,
        recent_tasks: list[str] | None = None,
    ) -> str:
        prompt_parts = [SYSTEM_PROMPT]

        if recent_memories:
            memory_lines = [f"- {memory}" for memory in recent_memories]
            prompt_parts.append("Recent memories:\n" + "\n".join(memory_lines))

        if recent_tasks:
            task_lines = [f"* {task}" for task in recent_tasks]
            prompt_parts.append("RECENT OPEN TASKS:\n" + "\n".join(task_lines))

        prompt_parts.append(f"User message:\n{user_message}")
        prompt_parts.append("Axion response:")

        return "\n\n".join(prompt_parts)
