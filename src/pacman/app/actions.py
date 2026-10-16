"""Shared application actions for Pac-Man."""

from enum import Enum, auto


class MainMenuAction(Enum):
    """Actions available from the Pac-Man main menu."""

    # Define the choices the UI can return to the orchestrator.
    START_GAME = auto()
    VIEW_HIGHSCORES = auto()
    SHOW_INSTRUCTIONS = auto()
    EXIT = auto()
