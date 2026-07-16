"""Main terminal application for Axion."""

from axion.agents.agent_manager import AgentManager
from axion.agents.plan_store import PlanStore
from axion.agents.planner_agent import PlannerAgent
from axion.ai.ai_core import AICore
from axion.ai.ollama_client import DEFAULT_MODEL
from axion.commands.router import CommandRouter
from axion.core.activity_log import log_activity
from axion.core.basic_responder import respond_to_chat
from axion.core.identity import AXION_NAME, AXION_TAGLINE, AXION_VERSION
from axion.memory.sqlite_memory import SQLiteMemory
from axion.projects.project_store import ProjectStore
from axion.tasks.task_store import TaskStore
from axion.tools.organizer import SmartOrganizer
from axion.tools.trash_manager import TrashManager
from axion.utils.text import divider
from axion.voice.speaker import speak_text


def is_valid_ai_response(response: str) -> bool:
    """Return True for any non-empty response that is not a clear error."""
    if not response:
        return False

    text = response.strip()
    if not text:
        return False

    return not is_error_response(text)


def is_error_response(response: str) -> bool:
    """Return True when the response is clearly an AI provider error."""
    text = response.strip().lower()
    error_markers = [
        "Ollama is not running",
        "Model not found",
        "Error:",
        "Failed to",
    ]
    return any(text.startswith(marker.lower()) for marker in error_markers)


class AxionApp:
    """A small terminal app that runs until the user exits."""

    def __init__(self) -> None:
        self.memory = SQLiteMemory()
        self.tasks = TaskStore()
        self.projects = ProjectStore()
        self.plan_store = PlanStore()
        self.trash_manager = TrashManager()
        self.organizer = SmartOrganizer()
        self.ai_core = AICore()
        self.agent_manager = AgentManager(
            self.plan_store,
            PlannerAgent(self.ai_core),
            self.tasks,
        )
        self.current_model = DEFAULT_MODEL
        self.voice_enabled = False
        self.router = CommandRouter(
            memory=self.memory,
            ai_core=self.ai_core,
            current_model=self.current_model,
            task_store=self.tasks,
            project_store=self.projects,
            voice_enabled=self.voice_enabled,
            plan_store=self.plan_store,
            agent_manager=self.agent_manager,
            trash_manager=self.trash_manager,
            organizer=self.organizer,
        )
        self.running = True

    def show_welcome(self) -> None:
        """Print the startup message."""
        print(divider())
        print(f"{AXION_NAME} v{AXION_VERSION}")
        print(AXION_TAGLINE)
        print()
        print("Type /help to see commands.")
        print(divider())

    def run(self) -> None:
        """Start the command loop."""
        self.memory.initialize()
        self.tasks.initialize()
        self.projects.initialize()
        self.plan_store.initialize()
        log_activity("app start")
        self.show_welcome()

        while self.running:
            try:
                user_input = input("axion> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                user_input = "/exit"

            if not user_input:
                continue

            if not user_input.startswith("/"):
                reply = self._handle_normal_chat(user_input)
                print(reply)
                if self.voice_enabled:
                    self._speak_normal_reply(reply)
                continue

            response = self.router.handle(user_input)
            self.current_model = self.router.current_model
            self.voice_enabled = self.router.voice_enabled
            if response.should_exit:
                self.running = False
                log_activity("app exit")

            if response.message:
                print(response.message)

    def _handle_normal_chat(self, user_message: str) -> str:
        """Send normal chat to the AI Core with fallback if needed."""
        from axion.commands.productivity_intents import translate_intent
        intent = translate_intent(user_message)
        if intent:
            return self.router.handle(intent).message if intent.startswith("/find-name") else intent
        log_activity("Routing normal message to AI Core", user_message)
        try:
            recent_memories = self._recent_memory_contents()
            response = self.ai_core.respond(
                user_message,
                recent_memories=recent_memories,
                model=self.current_model,
                recent_tasks=self._recent_open_task_titles(),
                active_projects=self._active_project_summaries(),
                active_agent_plans=self._active_agent_plan_context(),
            )
        except Exception as error:
            return self._fallback_response(user_message, f"AI Core error: {error}")

        if not is_valid_ai_response(response):
            return self._fallback_response(
                user_message,
                self._fallback_reason_for_response(response),
            )

        return response.strip()

    def _recent_memory_contents(self, limit: int = 5) -> list[str]:
        """Return recent memories for AI context when available."""
        try:
            memories = self.memory.list_memories()
        except Exception:
            return []

        return [memory.content for memory in memories[:limit]]

    def _recent_open_task_titles(self, limit: int = 5) -> list[str]:
        """Return recent open task titles for AI context when available."""
        try:
            tasks = self.tasks.list_tasks("open")
        except Exception:
            return []

        return [task.title for task in tasks[:limit]]

    def _active_project_summaries(self, limit: int = 5) -> list[str]:
        """Return active project summaries for AI context when available."""
        try:
            projects = self.projects.list_projects("active")
        except Exception:
            return []

        summaries = []
        for project in projects[:limit]:
            if project.description:
                summaries.append(f"{project.name}: {project.description}")
            else:
                summaries.append(project.name)

        return summaries

    def _active_agent_plan_context(self, limit: int = 3) -> list[str]:
        """Return active plan context for AI chat when available."""
        try:
            return self.plan_store.get_active_plan_context(limit)
        except Exception:
            return []

    def _fallback_response(self, user_message: str, reason: object) -> str:
        """Use the basic responder and log why the fallback was needed."""
        log_activity("Using fallback basic_responder because", str(reason))
        return respond_to_chat(user_message)

    def _speak_normal_reply(self, reply: str) -> None:
        """Speak normal chat replies when voice mode is enabled."""
        result = speak_text(reply)
        if result.success:
            log_activity("voice spoken", "normal chat reply")
            return

        log_activity("voice failed", result.message)
        print(f"Voice output failed: {result.message}")

    def _fallback_reason_for_response(self, response: str) -> str:
        """Return a clear log reason for an invalid AI Core response."""
        if not isinstance(response, str) or not response.strip():
            return "empty AI Core response"

        return response.strip()
