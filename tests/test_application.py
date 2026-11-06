"""Tests for the Pac-Man application orchestrator."""

import pytest

from pacman.app.actions import CharSelectAction, MainMenuAction
from pacman.app.application import AppState, PacManApp
from pacman.config.models import GameConfig, LevelConfig
from pacman.maze.direction import Direction
from pacman.game.ghost import GhostState
from pacman.game.pacgum import PacgumType
from types import SimpleNamespace
from pacman.app import application as application_module


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


def test_frightened_ghosts_after_super_pacgum() -> None:
    """Verify that ghosts are frightened after super-pacgum is obtained."""

    # Start a game so the application has an active level and player.
    app = PacManApp(_test_config())
    app.start_new_game()

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
    app.active_level.pacgums[destination] = PacgumType.SUPER_PACGUM

    # Move the player onto the super-pacgum.
    moved = app.move_player(direction)

    assert moved is True

    # Verify that all ghosts have changed state to frightened.
    for ghost in app.active_level.ghosts:
        assert ghost.state == GhostState.FRIGHTENED


def test_game_loop_advances_timers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that gameplay timers advance with real elapsed time."""

    # Create an active game with frightened ghosts.
    app = PacManApp(_test_config())
    app.start_new_game()

    assert app.active_level is not None
    level = app.active_level
    level.frighten_ghosts()

    # Simulate four frames spanning 2.2 seconds.
    timestamps = iter([0.0, 0.4, 1.1, 1.6, 2.2])

    # Group replacement clock functions without waiting for real time.
    fake_time = SimpleNamespace(
        monotonic=lambda: next(timestamps),
        time=lambda: 0.0,
        sleep=lambda seconds: None,
    )

    # monkeyp temporarily replaces functions and restores them after testing.
    # Disable unrelated UI operations while keeping the real game loop running.
    monkeypatch.setattr(application_module, "time", fake_time)
    monkeypatch.setattr(app, "_load_bg", lambda: None)
    monkeypatch.setattr(app, "_get_events", lambda: None)
    monkeypatch.setattr(application_module.pg.display, "flip", lambda: None)

    frames = 0

    def stop_after_four_frames() -> None:
        """Stop the application after four gameplay frames."""
        nonlocal frames

        # Modify the frame counter belonging to the enclosing test.
        frames += 1

        if frames == 4:
            app.stop()

    # Replace gameplay rendering with a helper that stops the continuous loop.
    monkeypatch.setattr(app, "_run_game", stop_after_four_frames)

    # Run the application using our simulated clock.
    app.run()

    # Only two complete seconds should have elapsed.
    assert level.remaining_time == 88
    assert level.frightened_timer == 4


def test_game_loop_preserves_time_during_pause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that pausing freezes timers without losing partial seconds."""

    app = PacManApp(_test_config())
    app.start_new_game()

    assert app.active_level is not None
    level = app.active_level
    level.frighten_ghosts()

    initial_time = level.remaining_time
    initial_frightened_time = level.frightened_timer

    # Simulate gameplay, a long pause, and resumed gameplay.
    timestamps = iter([
        0.0,   # Initial clock reading.
        0.4,   # Playing: 0.4 seconds accumulated.
        1.2,   # Playing: first complete second.
        1.8,   # Playing: 0.8 seconds accumulated.
        2.0,   # Pause: do not count this frame.
        12.0,  # Still paused after ten seconds.
        12.1,  # Resume: do not count paused time.
        12.5,  # Playing: accumulated time reaches 1.2 seconds.
    ])

    fake_time = SimpleNamespace(
        monotonic=lambda: next(timestamps),
        time=lambda: 0.0,
        sleep=lambda seconds: None,
    )

    monkeypatch.setattr(application_module, "time", fake_time)
    monkeypatch.setattr(app, "_load_bg", lambda: None)
    monkeypatch.setattr(app, "_run_game", lambda: None)
    monkeypatch.setattr(app, "_run_pause_menu", lambda: None)
    monkeypatch.setattr(
        application_module.pg.display,
        "flip",
        lambda: None,
    )

    frames = 0

    def simulate_events() -> None:
        """Pause, resume, and stop at specific simulated frames."""
        nonlocal frames
        frames += 1

        if frames == 4:
            app.pause_game()

        elif frames == 5:
            # Ten seconds have passed, but gameplay time is frozen.
            assert app.state == AppState.PAUSED
            assert level.remaining_time == initial_time - 1
            assert level.frightened_timer == initial_frightened_time - 1

        elif frames == 6:
            app.resume_game()

        elif frames == 7:
            app.stop()

    monkeypatch.setattr(app, "_get_events", simulate_events)

    app.run()

    # Two complete gameplay seconds, excluding time spent paused.
    assert level.remaining_time == initial_time - 2
    assert level.frightened_timer == initial_frightened_time - 2
    assert app.state == AppState.PLAYING


def test_game_loop_resets_time_when_level_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that a new level starts with no accumulated gameplay time."""

    app = PacManApp(_test_config())
    app.start_new_game()

    assert app.active_level is not None
    original_level = app.active_level
    initial_time = original_level.remaining_time

    # Accumulate 0.8 seconds, replace the level, then play another 1.2.
    timestamps = iter([
        0.0,  # Initial clock reading.
        0.4,  # Playing: 0.4 seconds accumulated.
        0.8,  # Playing: 0.8 seconds accumulated.
        1.6,  # Replace level: discard the transition frame.
        2.0,  # New level: 0.4 seconds accumulated.
        2.5,  # New level: 0.9 seconds accumulated.
        2.8,  # New level: 1.2 seconds, one complete tick.
    ])

    fake_time = SimpleNamespace(
        monotonic=lambda: next(timestamps),
        time=lambda: 0.0,
        sleep=lambda seconds: None,
    )

    monkeypatch.setattr(application_module, "time", fake_time)
    monkeypatch.setattr(app, "_load_bg", lambda: None)
    monkeypatch.setattr(app, "_run_game", lambda: None)
    monkeypatch.setattr(
        application_module.pg.display,
        "flip",
        lambda: None,
    )

    frames = 0

    def simulate_events() -> None:
        """Replace the active level during the simulated game loop."""
        nonlocal frames
        frames += 1

        if frames == 3:
            app.start_new_game()

        elif frames == 6:
            app.stop()

    monkeypatch.setattr(app, "_get_events", simulate_events)

    app.run()

    assert app.active_level is not None
    assert app.active_level is not original_level

    # The original level never completed its first second.
    assert original_level.remaining_time == initial_time

    # The replacement level receives exactly one complete second.
    assert app.active_level.remaining_time == initial_time - 1


def test_pause_and_resume_game() -> None:
    """Check that the pause/resume changes app state."""

    # Create the application in its initial state and start new game.
    app = PacManApp(_test_config())
    app.start_new_game()

    # Assert that game is running
    assert app.state == AppState.PLAYING

    # Set application state to PAUSED, and then assert.
    app.pause_game()

    assert app.state == AppState.PAUSED

    # Set application state to PLAYING, and then assert.
    app.resume_game()

    assert app.state == AppState.PLAYING
