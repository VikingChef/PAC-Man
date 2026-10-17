"""Pac-Man application entry point."""

import sys
from pathlib import Path

from pacman.app.application import PacManApp
from pacman.config.loader import load_config
import pygame as pg


def main() -> None:
    """Start the Pac-Man application."""

    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json", file=sys.stderr)
        return

    config_path = Path(sys.argv[1])

    try:
        config = load_config(config_path)
    except RuntimeError as error:
        print(error)
        return

    app = PacManApp(config)
    pg.init()
    app.run()
    pg.quit()


if __name__ == "__main__":
    main()
