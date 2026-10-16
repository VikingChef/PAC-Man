"""Tests for the Pac-Man application orchestrator."""

from pacman.app.application import AppState, PacManApp
from pacman.config.models import GameConfig, LevelConfig
from pacman.app.actions import MainMenuAction


def _test_config() -> GameConfig:
    """Return a valid configuration for application tests."""

    # Build a minimal valid configuration without using the JSON loader.
    return GameConfig(
        highscore_filename="highscores.json",
        lives=3,
        pacgum=42,
        points_per_pacgum=10,
        points_per_super_pacgum=50,
        points_per_ghost=200,
        seed=42,
        level_max_time=90,
        levels=[
            LevelConfig(
                number=1,
                width=21,
                height=21,
            )
        ],
    )


def test_app_starts_in_main_menu() -> None:
    """Check the initial application state."""

    # Create a fresh application with a valid test configuration.
    app = PacManApp(_test_config())

    # Confirm the application starts cleanly in the main menu.
    assert app.state == AppState.MAIN_MENU
    assert app.running is True
    assert app.game_state is None


def test_start_new_game_creates_game_state() -> None:
    """Check that starting a new game creates fresh run state."""

    # Create the application before any game has started.
    app = PacManApp(_test_config())

    # Start a new game using the configured default values.
    app.start_new_game()

    # Confirm the run state was created correctly.
    assert app.game_state is not None
    assert app.game_state.score == 0
    assert app.game_state.lives == 3
    assert app.game_state.current_level == 1
    assert app.game_state.remaining_time == 90
    assert app.state == AppState.PLAYING


def test_change_state_updates_application_state() -> None:
    """Check that the application state can be changed."""

    # Create the application in its initial state.
    app = PacManApp(_test_config())

    # Change to another valid application state.
    app.change_state(AppState.HIGHSCORES)

    # Confirm the new state was stored.
    assert app.state == AppState.HIGHSCORES


def test_stop_ends_application_loop() -> None:
    """Check that stopping the application ends its main loop."""

    # Create a running application.
    app = PacManApp(_test_config())

    # Stop the application cleanly.
    app.stop()

    # Confirm the main loop has been marked to stop.
    assert app.running is False


def test_start_game_action_starts_new_game() -> None:
    """Check that Start Game creates a new run."""

    # Create the application before a game has started.
    app = PacManApp(_test_config())

    # Handle the Start Game choice from the main menu.
    app._handle_main_menu_action(MainMenuAction.START_GAME)

    # Confirm a new game was created and gameplay began.
    assert app.game_state is not None
    assert app.state == AppState.PLAYING


def test_highscores_action_opens_highscores() -> None:
    """Check that the Highscores choice opens the highscore screen."""

    # Create the application in the main menu.
    app = PacManApp(_test_config())

    # Handle the Highscores choice from the main menu.
    app._handle_main_menu_action(MainMenuAction.VIEW_HIGHSCORES)

    # Confirm the application moved to the highscore state.
    assert app.state == AppState.HIGHSCORES


def test_instructions_action_opens_instructions() -> None:
    """Check that the Instructions choice opens the instructions screen."""

    # Create the application in the main menu.
    app = PacManApp(_test_config())

    # Handle the Instructions choice from the main menu.
    app._handle_main_menu_action(MainMenuAction.SHOW_INSTRUCTIONS)

    # Confirm the application moved to the instructions state.
    assert app.state == AppState.INSTRUCTIONS


def test_exit_action_stops_application() -> None:
    """Check that the Exit choice stops the application."""

    # Create a running application.
    app = PacManApp(_test_config())

    # Handle the Exit choice from the main menu.
    app._handle_main_menu_action(MainMenuAction.EXIT)

    # Confirm the application was stopped cleanly.
    assert app.running is False
