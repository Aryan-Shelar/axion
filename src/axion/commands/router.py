"""Route user input to Axion commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from axion.core.activity_log import log_activity
from axion.core.basic_responder import respond_to_chat
from axion.core.identity import (
    AXION_NAME,
    AXION_PERSONALITY,
    AXION_TAGLINE,
    AXION_VERSION,
)
from axion.core.status import build_status
from axion.memory.sqlite_memory import SQLiteMemory
from axion.tools.browser import open_url
from axion.tools.folder_opener import open_folder


@dataclass(frozen=True)
class CommandResponse:
    """A command result that the terminal app can print or act on."""

    message: str
    should_exit: bool = False


class CommandRouter:
    """Handle slash commands and placeholder chat input."""

    def __init__(self, memory: SQLiteMemory) -> None:
        self.memory = memory

    def handle(self, user_input: str) -> CommandResponse:
        """Route input to a command handler."""
        if not user_input.startswith("/"):
            return CommandResponse(respond_to_chat(user_input))

        command, _, argument = user_input.partition(" ")
        command = command.lower()
        argument = argument.strip()
        log_activity("command used", command)

        if command == "/help":
            return CommandResponse(self._help_text())
        if command == "/exit":
            return CommandResponse("Goodbye from Axion.", should_exit=True)
        if command == "/time":
            return CommandResponse(self._current_time())
        if command == "/remember":
            return self._remember(argument)
        if command == "/memories":
            return self._list_memories()
        if command == "/note":
            return self._add_note(argument)
        if command == "/notes":
            return self._list_notes()
        if command == "/open":
            return self._open_url(argument)
        if command == "/folder":
            return self._open_folder(argument)
        if command == "/whoami":
            return CommandResponse(self._whoami())
        if command == "/status":
            return CommandResponse(build_status(self.memory))
        if command == "/clear":
            return CommandResponse("\033[2J\033[HScreen cleared.")
        if command == "/search-memory":
            return self._search_memories(argument)
        if command == "/search-notes":
            return self._search_notes(argument)

        return CommandResponse(f"Unknown command: {command}. Type /help for options.")

    def _help_text(self) -> str:
        return "\n".join(
            [
                "Axion commands:",
                "/help - Show this help message",
                "/exit - Exit Axion",
                "/time - Show the current local time",
                "/remember <text> - Save a memory",
                "/memories - List saved memories",
                "/search-memory <keyword> - Search saved memories",
                "/note <title> :: <content> - Save a note",
                "/notes - List saved notes",
                "/search-notes <keyword> - Search saved notes",
                "/open <url> - Open a website in your default browser",
                "/folder <path> - Open a folder on your computer",
                "/whoami - Show Axion's identity",
                "/status - Show Axion system status",
                "/clear - Clear the terminal screen",
            ]
        )

    def _current_time(self) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"Current local time: {now}"

    def _remember(self, content: str) -> CommandResponse:
        if not content:
            return CommandResponse("Usage: /remember <text>")

        memory_id = self.memory.add_memory(content)
        log_activity("memory saved", f"id={memory_id}")
        return CommandResponse(f"Memory saved with id {memory_id}.")

    def _list_memories(self) -> CommandResponse:
        memories = self.memory.list_memories()
        if not memories:
            return CommandResponse("No memories saved yet.")

        lines = ["Saved memories:"]
        for memory in memories:
            lines.append(f"{memory.id}. {memory.content} ({memory.created_at})")

        return CommandResponse("\n".join(lines))

    def _search_memories(self, keyword: str) -> CommandResponse:
        if not keyword:
            return CommandResponse("Usage: /search-memory <keyword>")

        memories = self.memory.search_memories(keyword)
        if not memories:
            return CommandResponse(f"No memories found for: {keyword}")

        lines = [f"Memory search results for '{keyword}':"]
        for memory in memories:
            lines.append(f"{memory.id}. {memory.content} ({memory.created_at})")

        return CommandResponse("\n".join(lines))

    def _add_note(self, argument: str) -> CommandResponse:
        if "::" not in argument:
            return CommandResponse("Usage: /note <title> :: <content>")

        title, content = [part.strip() for part in argument.split("::", 1)]
        if not title or not content:
            return CommandResponse("Usage: /note <title> :: <content>")

        note_id = self.memory.add_note(title, content)
        log_activity("note saved", f"id={note_id}")
        return CommandResponse(f"Note saved with id {note_id}.")

    def _list_notes(self) -> CommandResponse:
        notes = self.memory.list_notes()
        if not notes:
            return CommandResponse("No notes saved yet.")

        lines = ["Saved notes:"]
        for note in notes:
            lines.append(f"{note.id}. {note.title}: {note.content} ({note.created_at})")

        return CommandResponse("\n".join(lines))

    def _search_notes(self, keyword: str) -> CommandResponse:
        if not keyword:
            return CommandResponse("Usage: /search-notes <keyword>")

        notes = self.memory.search_notes(keyword)
        if not notes:
            return CommandResponse(f"No notes found for: {keyword}")

        lines = [f"Note search results for '{keyword}':"]
        for note in notes:
            lines.append(f"{note.id}. {note.title}: {note.content} ({note.created_at})")

        return CommandResponse("\n".join(lines))

    def _open_url(self, argument: str) -> CommandResponse:
        message = open_url(argument)
        if message.startswith("Opened "):
            log_activity("url opened", message.removeprefix("Opened "))

        return CommandResponse(message)

    def _open_folder(self, argument: str) -> CommandResponse:
        if not argument:
            return CommandResponse("Usage: /folder <path>")

        message = open_folder(argument)
        if message.startswith("Opened folder: "):
            log_activity("folder opened", message.removeprefix("Opened folder: "))

        return CommandResponse(message)

    def _whoami(self) -> str:
        return "\n".join(
            [
                f"{AXION_NAME} v{AXION_VERSION}",
                AXION_TAGLINE,
                AXION_PERSONALITY,
            ]
        )
