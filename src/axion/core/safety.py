"""Basic action safety classification for future automation."""

SAFE_ACTIONS = {
    "open_url",
    "open_folder",
    "remember",
    "note",
    "list",
}

NEEDS_CONFIRMATION_ACTIONS = {
    "run_command",
    "edit_file",
    "move_file",
}

BLOCKED_ACTIONS = {
    "delete_file",
    "format_disk",
    "reveal_secrets",
}


def classify_action(action_name: str) -> str:
    """Classify a future action as safe, needs confirmation, or blocked."""
    normalized = action_name.strip().lower()

    if normalized in SAFE_ACTIONS:
        return "safe"
    if normalized in NEEDS_CONFIRMATION_ACTIONS:
        return "needs_confirmation"
    if normalized in BLOCKED_ACTIONS:
        return "blocked"

    return "needs_confirmation"
