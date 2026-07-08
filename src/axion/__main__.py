"""Run Axion with: python -m axion."""

from axion.core.app import AxionApp


def main() -> None:
    """Start the Axion terminal app."""
    app = AxionApp()
    app.run()


if __name__ == "__main__":
    main()

