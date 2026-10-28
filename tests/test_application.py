"""Tests for the Pac-Man application orchestrator."""

from pacman.app.actions import MainMenuAction
from pacman.app.application import AppState, PacManApp
from pacman.config.models import GameConfig, LevelConfig
from pacman.maze.direction import Direction


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


def test_move_player_moves_active_player() -> None:
    """Verify that the app delegates movement to the active player."""

    # Start a game so the application has an active level and player.
    app = PacManApp(_test_config())
    app.start_new_game()

    # Keep the test explicit about the state required for gameplay.
    assert app.active_level is not None

    player = app.active_level.player
    maze = app.active_level.maze

    # Find one direction the generated maze allows from the spawn position.
    direction = next(
        direction
        for direction in Direction
        if maze.can_move(player.position, direction)
    )

    start_position = player.position

    # Move through application boundary instead of touching Player directly.
    moved = app.move_player(direction)

    # The app should report success and the player's position should change.
    assert moved is True
    assert player.position != start_position
    assert player.direction == direction


def test_advance_level_creates_next_level() -> None:
    """Verify that advancing creates the next configured level."""

    # Extend the standard test configuration with a second playable level.
    config = _test_config()

    config.levels.append(
        LevelConfig(
            number=2,
            width=21,
            height=21,
        )
    )

    # Start a game on level one and keep its Level object for comparison.
    app = PacManApp(config)
    app.start_new_game()

    first_level = app.active_level

    # Advance from level one into the next configured level.
    app._advance_level()

    # Progression should update the run state and replace the active Level.
    assert app.game_state is not None
    assert app.game_state.current_level == 2
    assert app.active_level is not first_level


def test_advance_level_reaches_victory_after_final_level() -> None:
    """Verify that advancing past the final level enters victory."""

    # Use the standard single-level configuration so level one is final.
    config = _test_config()

    # Start a game on the only configured level.
    app = PacManApp(config)
    app.start_new_game()

    # Attempt to advance after completing the final level.
    app._advance_level()

    # Final-level progression should enter the victory state.
    assert app.state == AppState.VICTORY
