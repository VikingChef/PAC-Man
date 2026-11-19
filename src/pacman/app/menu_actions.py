
"""Actions returned by the main menu and character selection."""

from enum import Enum, auto


class MainMenuAction(Enum):
    """Actions available from the Pac-Man main menu."""

    # Define the choices the UI can return to the orchestrator.
    START_GAME = auto()
    VIEW_HIGHSCORES = auto()
    SHOW_INSTRUCTIONS = auto()
    EXIT = auto()


class CharSelectAction(Enum):
    """Actions available from the Character Select menu."""

    MAIN_MENU = auto()
    WAKA_WAKA_WANDA = auto()
    MS_POWER_PELLET = auto()
