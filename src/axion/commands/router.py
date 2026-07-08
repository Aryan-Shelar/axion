"""Route user input to Axion commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from axion.ai.ai_core import AICore
from axion.ai.ollama_client import DEFAULT_MODEL
from axion.core.activity_log import log_activity
from axion.core.identity import (
    AXION_NAME,
    AXION_PERSONALITY,
    AXION_TAGLINE,
    AXION_VERSION,
)
from axion.core.status import build_status
from axion.memory.sqlite_memory import SQLiteMemory
from axion.tasks.task_store import TaskItem, TaskStore
from axion.tools.app_launcher import launch_app, list_app_shortcuts
from axion.tools.browser import open_url
from axion.tools.folder_opener import open_folder


@dataclass(frozen=True)
class CommandResponse:
    """A command result that the terminal app can print or act on."""

    message: str
    should_exit: bool = False


class CommandRouter:
    """Handle Axion slash commands."""

    def __init__(
        self,
        memory: SQLiteMemory,
        ai_core: AICore | None = None,
        current_model: str = DEFAULT_MODEL,
        task_store: TaskStore | None = None,
    ) -> None:
        self.memory = memory
        self.ai_core = ai_core or AICore()
        self.current_model = current_model
        self.task_store = task_store or TaskStore()

    def handle(self, user_input: str) -> CommandResponse:
        """Route input to a command handler."""
        if not user_input.startswith("/"):
            return CommandResponse("Normal chat is handled by the Axion app.")

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
        if command == "/apps":
            return CommandResponse(self._apps())
        if command == "/app":
            return self._app(argument)
        if command == "/task":
            return self._task_command(argument)
        if command == "/tasks":
            return self._tasks_command(argument)
        if command == "/whoami":
            return CommandResponse(self._whoami())
        if command == "/status":
            ollama_available = self.ai_core.is_available()
            return CommandResponse(
                build_status(
                    self.memory,
                    self.current_model,
                    ollama_available,
                    self.task_store,
                )
            )
        if command == "/clear":
            return CommandResponse("\033[2J\033[HScreen cleared.")
        if command == "/search-memory":
            return self._search_memories(argument)
        if command == "/search-notes":
            return self._search_notes(argument)
        if command == "/ai-status":
            return CommandResponse(self._ai_status())
        if command == "/model":
            return self._model_command(argument)

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
                "/app <name> - Open an allowlisted app",
                "/apps - List available app shortcuts",
                "/task add <title> - Save a task",
                "/tasks - List all tasks",
                "/tasks open - List open tasks",
                "/tasks done - List completed tasks",
                "/task done <id> - Mark a task done",
                "/task delete <id> - Delete a task",
                "/whoami - Show Axion's identity",
                "/status - Show Axion system status",
                "/ai-status - Show local AI Core status",
                "/model - Show the current AI model",
                "/model <name> - Change the current AI model",
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

    def _apps(self) -> str:
        shortcuts = ", ".join(list_app_shortcuts())
        return f"Available apps: {shortcuts}"

    def _app(self, argument: str) -> CommandResponse:
        if not argument:
            return CommandResponse("Usage: /app <name>")

        message, launched = launch_app(argument)
        if launched:
            log_activity("app launched", argument.strip().lower())
        else:
            log_activity("app launch failed", f"{argument}: {message}")

        return CommandResponse(message)

    def _task_command(self, argument: str) -> CommandResponse:
        action, _, value = argument.partition(" ")
        action = action.lower().strip()
        value = value.strip()

        if action == "add":
            return self._task_add(value)
        if action == "done":
            return self._task_done(value)
        if action == "delete":
            return self._task_delete(value)

        return CommandResponse(
            "Usage: /task add <title>, /task done <id>, or /task delete <id>"
        )

    def _tasks_command(self, argument: str) -> CommandResponse:
        status = argument.lower().strip() or None
        if status not in {None, "open", "done"}:
            return CommandResponse("Usage: /tasks, /tasks open, or /tasks done")

        tasks = self.task_store.list_tasks(status)
        if not tasks:
            if status:
                return CommandResponse(f"No {status} tasks.")
            return CommandResponse("No tasks saved yet.")

        return CommandResponse(self._format_tasks(tasks))

    def _task_add(self, title: str) -> CommandResponse:
        if not title:
            return CommandResponse("Usage: /task add <title>")

        task_id = self.task_store.add_task(title)
        log_activity("task added", f"id={task_id}")
        return CommandResponse(f"Task saved with id {task_id}.")

    def _task_done(self, value: str) -> CommandResponse:
        task_id = self._parse_task_id(value)
        if task_id is None:
            return CommandResponse("Usage: /task done <id>")

        if not self.task_store.complete_task(task_id):
            return CommandResponse(f"Task {task_id} was not found.")

        log_activity("task completed", f"id={task_id}")
        return CommandResponse(f"Task {task_id} marked done.")

    def _task_delete(self, value: str) -> CommandResponse:
        task_id = self._parse_task_id(value)
        if task_id is None:
            return CommandResponse("Usage: /task delete <id>")

        if not self.task_store.delete_task(task_id):
            return CommandResponse(f"Task {task_id} was not found.")

        log_activity("task deleted", f"id={task_id}")
        return CommandResponse(f"Task {task_id} deleted.")

    def _parse_task_id(self, value: str) -> int | None:
        try:
            task_id = int(value)
        except ValueError:
            return None

        if task_id < 1:
            return None

        return task_id

    def _format_tasks(self, tasks: list[TaskItem]) -> str:
        lines = ["Tasks:"]
        for task in tasks:
            lines.append(f"{task.id}. [{task.status}] {task.title}")

        return "\n".join(lines)

    def _whoami(self) -> str:
        return "\n".join(
            [
                f"{AXION_NAME} v{AXION_VERSION}",
                AXION_TAGLINE,
                AXION_PERSONALITY,
            ]
        )

    def _ai_status(self) -> str:
        available_text = "yes" if self.ai_core.is_available() else "no"
        return "\n".join(
            [
                "AI Core status:",
                "Provider: Ollama",
                f"Current model: {self.current_model}",
                f"Ollama available: {available_text}",
            ]
        )

    def _model_command(self, argument: str) -> CommandResponse:
        if not argument:
            return CommandResponse(f"Current model: {self.current_model}")

        self.current_model = argument
        log_activity("Model changed", self.current_model)
        return CommandResponse(f"Current model set to: {self.current_model}")
