"""Pac-Man application entry point."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from pacman.app.application import PacManApp
from pacman.config.loader import load_config, GameConfig


def main() -> None:
    """Start the Pac-Man application."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json", file=sys.stderr)
        sys.exit(1)

    config_path: Path = Path(sys.argv[1])

    try:
        config: GameConfig = load_config(config_path)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    with PacManApp(config) as app:
        app.run()


if __name__ == "__main__":
    main()
