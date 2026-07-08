"""Main terminal application for Axion."""

from axion.commands.router import CommandRouter
from axion.core.activity_log import log_activity
from axion.core.identity import AXION_NAME, AXION_TAGLINE, AXION_VERSION
from axion.memory.sqlite_memory import SQLiteMemory
from axion.utils.text import divider


class AxionApp:
    """A small terminal app that runs until the user exits."""

    def __init__(self) -> None:
        self.memory = SQLiteMemory()
        self.router = CommandRouter(self.memory)
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

            response = self.router.handle(user_input)
            if response.should_exit:
                self.running = False
                log_activity("app exit")

            if response.message:
                print(response.message)
