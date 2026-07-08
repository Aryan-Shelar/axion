"""Simple fallback response for normal chat when the AI Core cannot answer."""


def respond_to_chat(message: str) -> str:
    """Return one generic fallback response for any normal text."""
    return (
        "I could not get a valid AI Core response. I can still help with memory, "
        "notes, folders, websites, and status commands. Type /help."
    )
