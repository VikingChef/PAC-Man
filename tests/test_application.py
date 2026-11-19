"""Test application states, menus, movement and progression."""

import pytest
import pygame as pg
from pacman.app.actions import CharSelectAction, MainMenuAction
from pacman.app.application import AppState, PacManApp
from pacman.config.models import LevelConfig
from pacman.maze.direction import Direction
from pacman.game.ghost import GhostState
from pacman.game.level import Level
from pacman.game.pacgum import PacgumType
from pacman.app import application as application_module
from tests.app_test_helpers import _test_config, _start_test_game


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
    _start_test_game(app)
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


def test_start_game_action_opens_character_select() -> None:
    """Check that Start Game opens character selection."""
    # Create the application before a game has started.
    app = PacManApp(_test_config())
    # Handle the Start Game choice from the main menu.
    app._handle_main_menu_action(MainMenuAction.START_GAME)
    # Character selection should happen before the game itself is created.
    assert app.game_state is None
    assert app.state == AppState.CHAR_SELECT


@pytest.mark.parametrize(
    "queen",
    [
        CharSelectAction.WAKA_WAKA_WANDA,
        CharSelectAction.MS_POWER_PELLET,
    ],
)
def test_character_select_action_starts_new_game(
    queen: CharSelectAction,
) -> None:
    """Check that choosing either character creates a new run."""
    # Create the application and enter character selection.
    app = PacManApp(_test_config())
    app._handle_main_menu_action(MainMenuAction.START_GAME)
    # Choose one of the playable characters.
    app._handle_char_select_action(queen)
    # Choosing either character should create the run and begin gameplay.
    assert app.queen_chosen == queen
    assert app.game_state is not None
    assert app.active_level is not None
    # Character selection starts the level introduction.
    # Gameplay begins only after the announcement finishes.
    assert app.state == AppState.LEVEL_INTRO


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
    _start_test_game(app)
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


def test_advance_level_creates_next_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify level progression uses a new seed and creates four ghosts."""

    config = _test_config()
    config.levels.append(
        LevelConfig(
            number=2,
            width=15,
            height=15,
        )
    )

    app = PacManApp(config)
    _start_test_game(app)

    first_level = app.active_level
    assert first_level is not None

    # Control the random value so the test is reproducible.
    next_seed = 123456
    random_calls: list[tuple[int, int]] = []

    def fake_randint(lower: int, upper: int) -> int:
        random_calls.append((lower, upper))
        return next_seed

    monkeypatch.setattr(application_module, "randint", fake_randint)

    # Record the seed passed to the real level factory.
    original_create_level = application_module.create_level
    received_seeds: list[int] = []

    def track_create_level(
        config: LevelConfig,
        seed: int,
        time_limit: int,
        pacgum_count: int,
        player_sprite: CharSelectAction,
    ) -> Level:
        received_seeds.append(seed)
        return original_create_level(
            config=config,
            seed=seed,
            time_limit=time_limit,
            pacgum_count=pacgum_count,
            player_sprite=player_sprite,
        )

    monkeypatch.setattr(
        application_module,
        "create_level",
        track_create_level,
    )

    app._advance_level()

    assert app.game_state is not None
    assert app.game_state.current_level == 2

    assert app.active_level is not None
    assert app.active_level is not first_level
    assert app.active_level.maze.width == 15
    assert app.active_level.maze.height == 15
    assert len(app.active_level.ghosts) == 4

    # Verify a new seed was requested and passed to level creation.
    assert random_calls == [(0, 2**31 - 1)]
    assert received_seeds == [next_seed]


def test_advance_level_reaches_victory_after_final_level() -> None:
    """Verify that advancing past the final level enters victory."""
    # Use the standard single-level configuration so level one is final.
    config = _test_config()
    # Start a game on the only configured level.
    app = PacManApp(config)
    _start_test_game(app)
    # Attempt to advance after completing the final level.
    app._advance_level()
    # Final-level progression should enter the victory state.
    assert app.state == AppState.VICTORY


def test_frightened_ghosts_after_super_pacgum() -> None:
    """Verify that ghosts are frightened after super-pacgum is obtained."""
    # Start a game so the application has an active level and player.
    app = PacManApp(_test_config())
    _start_test_game(app)
    # Keep the test explicit about the state required for gameplay.
    assert app.active_level is not None
    player = app.active_level.player
    maze = app.active_level.maze
    # Find a direction the player can move from the starting position.
    direction = next(
        direction
        for direction in Direction
        if maze.can_move(player.position, direction)
    )
    # Get the horizontal and vertical movement offsets.
    dx, dy = direction.value
    # Calculate the cell directly ahead of the player.
    x, y = player.position
    destination = (x + dx, y + dy)
    # Place a super-pacgum at the player's next position.
    app.active_level.pacgums[destination] = (
        PacgumType.SUPER_PACGUM, pg.Surface((1, 1))
    )
    # Move the player onto the super-pacgum.
    moved = app.move_player(direction)
    assert moved is True
    # Verify that all ghosts have changed state to frightened.
    for ghost in app.active_level.ghosts:
        assert ghost.state == GhostState.FRIGHTENED


def test_pause_and_resume_game() -> None:
    """Check that the pause/resume changes app state."""
    # Create the application in its initial state and start new game.
    app = PacManApp(_test_config())
    _start_test_game(app)
    # Assert that game is running
    assert app.state == AppState.PLAYING
    # Set application state to PAUSED, and then assert.
    app.pause_game()
    assert app.state == AppState.PAUSED
    # Set application state to PLAYING, and then assert.
    app.resume_game()
    assert app.state == AppState.PLAYING
