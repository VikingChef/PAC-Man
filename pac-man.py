"""Pac-Man application entry point."""

import sys
from pathlib import Path


def main() -> None:
    """Start the Pac-Man application."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json", file=sys.stderr)
        sys.exit(1)

    # Make the src package available for direct command-line launches.
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

    from pacman.app.application import PacManApp
    from pacman.config.loader import load_config, GameConfig

    config_path: Path = Path(sys.argv[1])

    try:
        config: GameConfig = load_config(config_path)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    try:
        # Run the game and release its resources on exit.
        with PacManApp(config) as app:
            app.run()
    except KeyboardInterrupt:
        # Handle Ctrl+C without displaying a traceback.
        print(
            "Game interrupted in terminal, exiting...",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
