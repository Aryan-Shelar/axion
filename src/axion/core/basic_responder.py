"""Simple responses for normal chat before the AI Core exists."""

from axion.core.identity import AXION_NAME


def respond_to_chat(message: str) -> str:
    """Return a helpful built-in response for normal text."""
    normalized = message.strip().lower()

    if normalized in {"hi", "hello", "hey"}:
        return (
            f"Hello. I am {AXION_NAME}. My AI Core is not connected yet, but I "
            "can already manage notes, memory, folders, and basic commands."
        )

    if "what can you do" in normalized or "help" in normalized:
        return (
            "I can remember information, save notes, open websites, open "
            "folders, and show system status. Type /help."
        )

    return (
        "I hear you. My AI Core is not connected yet, but I can still help with "
        "memory, notes, folders, websites, and status commands. Type /help."
    )
