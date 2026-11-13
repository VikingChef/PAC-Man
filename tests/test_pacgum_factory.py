"""Tests for the Pac-Man application orchestrator."""
from types import SimpleNamespace

import pytest
import pygame as pg

from pacman.app.actions import CharSelectAction, MainMenuAction
from pacman.app.application import AppState, PacManApp
from pacman.config.models import GameConfig, LevelConfig
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall
from pacman.game.cheat_mode import CheatMode
from pacman.game.ghost import Ghost, GhostIdentity, GhostState
from pacman.game.level import Level
from pacman.game.player import Player
from pacman.game.state import GameState
from pacman.game.pacgum import PacgumType
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


def _start_test_game(app: PacManApp) -> None:
    """Choose a test character before starting the gameplay run."""
    # Application tests start gameplay directly instead of clicking through
    # the character selection screen. Supply the same valid choice the UI
    # would normally provide, while keeping character selection required.
    app.change_queen(CharSelectAction.WAKA_WAKA_WANDA)
    app.start_new_game()


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
    _start_test_game(app)
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


def test_game_loop_advances_timers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that gameplay timers advance with real elapsed time."""
    # Create an active game with frightened ghosts.
    app = PacManApp(_test_config())
    _start_test_game(app)
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
    _start_test_game(app)
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
    _start_test_game(app)
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
            _start_test_game(app)
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
    _start_test_game(app)
    # Assert that game is running
    assert app.state == AppState.PLAYING
    # Set application state to PAUSED, and then assert.
    app.pause_game()
    assert app.state == AppState.PAUSED
    # Set application state to PLAYING, and then assert.
    app.resume_game()
    assert app.state == AppState.PLAYING


def create_collision_test_app(
    ghost_states: list[GhostState],
    lives: int = 3,
) -> PacManApp:
    """Build a logic-only application with ghosts occupying Pac-Man's cell."""
    # Avoid initializing a Pygame window; the resolver does not need one.
    app = PacManApp.__new__(PacManApp)
    app.config = _test_config()
    app.cheat_mode = CheatMode()
    app.game_state = GameState(score=0, lives=lives, current_level=1)
    app.state = AppState.PLAYING
    app.visual_move_start = None
    app.visual_move_end = None
    app.ghost_visual_moves = {}

    maze = Maze([
        [Wall.NONE for _ in range(3)]
        for _ in range(3)
    ])
    player = Player(
        spawn_position=(1, 1),
        spawn_direction=Direction.EAST,
    )
    identities = list(GhostIdentity)
    ghosts: list[Ghost] = []

    for index, state in enumerate(ghost_states):
        ghost = Ghost(
            spawn_position=(1, 1),
            identity=identities[index],
            spawn_direction=Direction.WEST,
        )
        ghost.state = state
        ghosts.append(ghost)

    app.active_level = Level(
        config=LevelConfig(number=1, width=3, height=3),
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=90,
        pacgums={},
    )
    return app


def test_frightened_collision_awards_points() -> None:
    """Eating a frightened ghost awards points and changes its state."""
    app = create_collision_test_app([GhostState.FRIGHTENED])

    app.resolve_ghost_collisions()

    assert app.game_state is not None
    assert app.active_level is not None
    assert app.game_state.score == 200
    assert app.game_state.lives == 3
    assert app.active_level.ghosts[0].state == GhostState.EATEN


def test_eaten_ghost_does_not_award_points_twice() -> None:
    """Repeated collision checks must not score an eaten ghost again."""
    app = create_collision_test_app([GhostState.FRIGHTENED])

    app.resolve_ghost_collisions()
    app.resolve_ghost_collisions()

    assert app.game_state is not None
    assert app.game_state.score == 200


def test_multiple_frightened_ghosts_award_points() -> None:
    """Each successfully eaten ghost awards its configured points."""
    app = create_collision_test_app([
        GhostState.FRIGHTENED,
        GhostState.FRIGHTENED,
    ])

    app.resolve_ghost_collisions()

    assert app.game_state is not None
    assert app.active_level is not None
    assert app.game_state.score == 400
    assert app.game_state.lives == 3
    for ghost in app.active_level.ghosts:
        assert ghost.state == GhostState.EATEN


def test_enraged_collision_takes_priority() -> None:
    """An enraged ghost causes life loss without awarding ghost points."""
    app = create_collision_test_app([
        GhostState.ENRAGED,
        GhostState.FRIGHTENED,
    ])

    app.resolve_ghost_collisions()

    assert app.game_state is not None
    assert app.active_level is not None
    assert app.game_state.lives == 2
    assert app.game_state.score == 0
    assert app.state == AppState.PLAYING
    # Life loss resets both ghosts to their normal state.
    for ghost in app.active_level.ghosts:
        assert ghost.state == GhostState.ENRAGED


def test_final_life_collision_ends_game() -> None:
    """An enraged collision on the last life triggers GAME_OVER."""
    app = create_collision_test_app([GhostState.ENRAGED], lives=1)

    app.resolve_ghost_collisions()

    assert app.game_state is not None
    assert app.game_state.lives == 0
    assert app.state == AppState.GAME_OVER


def test_player_movement_into_enraged_ghost_loses_life() -> None:
    """Verify that moving into an enraged ghost costs one life."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    assert app.active_level is not None
    assert app.game_state is not None

    level = app.active_level
    player = level.player
    ghost = level.ghosts[0]
    # Find a legal movement direction and place a ghost in that cell.
    direction = next(
        direction for direction in Direction
        if level.maze.can_move(player.position, direction)
    )
    dx, dy = direction.value
    x, y = player.position
    destination = (x + dx, y + dy)
    ghost.position = destination
    ghost.state = GhostState.ENRAGED
    # Prevent a super-pacgum from frightening the ghost first.
    level.pacgums[destination] = (
        PacgumType.PACGUM, pg.Surface((1, 1))
    )

    moved = app.move_player(direction)
    assert moved is True
    assert app.game_state.lives == 2
    assert app.state == AppState.PLAYING
    assert player.position == player.spawn_position
    assert ghost.position == ghost.spawn_position
    assert ghost.state == GhostState.ENRAGED


def test_super_pacgum_activates_before_ghost_collision() -> None:
    """Verify a super-pacgum makes a ghost edible before collision."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    assert app.active_level is not None
    assert app.game_state is not None

    level = app.active_level
    player = level.player
    ghost = level.ghosts[0]
    direction = next(
        direction for direction in Direction
        if level.maze.can_move(player.position, direction)
    )
    dx, dy = direction.value
    x, y = player.position
    destination = (x + dx, y + dy)
    # The super-pacgum must be collected before resolving the ghost collision.
    ghost.position = destination
    ghost.state = GhostState.ENRAGED
    level.pacgums[destination] = (
        PacgumType.SUPER_PACGUM, pg.Surface((1, 1))
    )

    moved = app.move_player(direction)
    assert moved is True
    expected_score = (
        app.config.points_per_super_pacgum
        + app.config.points_per_ghost
    )
    assert app.game_state.score == expected_score
    assert app.game_state.lives == 3
    assert app.state == AppState.PLAYING
    assert ghost.state == GhostState.EATEN
    assert ghost.respawn_timer == 5
    assert level.frightened_timer == 6
    assert destination not in level.pacgums


def test_game_loop_enters_timeout_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that timer expiry stops gameplay and ghost movement."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    assert app.active_level is not None
    level = app.active_level
    level.remaining_time = 1

    timestamps = iter([0.0, 1.1, 1.2])
    fake_time = SimpleNamespace(
        monotonic=lambda: next(timestamps),
        time=lambda: 0.0,
        sleep=lambda seconds: None,
    )
    monkeypatch.setattr(application_module, "time", fake_time)
    monkeypatch.setattr(app, "_load_bg", lambda: None)
    monkeypatch.setattr(app, "_run_game", lambda: None)
    monkeypatch.setattr(application_module.pg.display, "flip", lambda: None)

    ghost_moves = 0

    def track_ghost_movement() -> None:
        """Count ghost movement calls without moving them."""
        nonlocal ghost_moves
        ghost_moves += 1

    monkeypatch.setattr(level, "move_ghosts", track_ghost_movement)
    frames = 0

    def simulate_events() -> None:
        """Stop the application after observing timeout."""
        nonlocal frames
        frames += 1
        if frames == 2:
            app.stop()

    monkeypatch.setattr(app, "_get_events", simulate_events)
    app.run()
    assert level.remaining_time == 0
    assert app.state == AppState.TIMEOUT
    assert ghost_moves == 0


def test_ghost_movement_collision_loses_one_life(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify ghost movement causes one collision and stops further moves."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    assert app.active_level is not None
    assert app.game_state is not None
    level = app.active_level
    ghost = level.ghosts[0]
    player = level.player
    movement_calls = 0

    def simulate_ghost_movement() -> None:
        """Simulate a ghost reaching Pac-Man's position."""
        nonlocal movement_calls
        movement_calls += 1
        ghost.position = player.position

    monkeypatch.setattr(level, "move_ghosts", simulate_ghost_movement)
    ghost_interval = level.config.ghost_move_interval_ms / 1000
    timestamps = iter([0.0, ghost_interval * 3 + 0.01])
    fake_time = SimpleNamespace(
        monotonic=lambda: next(timestamps),
        time=lambda: 0.0,
        sleep=lambda seconds: None,
    )
    monkeypatch.setattr(application_module, "time", fake_time)
    monkeypatch.setattr(app, "_load_bg", lambda: None)
    monkeypatch.setattr(app, "_get_events", lambda: None)
    monkeypatch.setattr(application_module.pg.display, "flip", lambda: None)
    monkeypatch.setattr(app, "_run_game", app.stop)
    app.run()

    assert app.game_state.lives == 2
    assert app.state == AppState.PLAYING
    assert player.position == player.spawn_position
    assert ghost.position == ghost.spawn_position
    assert movement_calls == 1


def test_timeout_deducts_one_life() -> None:
    """Verify that timeout costs one life and restarts gameplay."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    assert app.game_state is not None
    starting_lives = app.game_state.lives
    app._finish_timeout()
    assert app.game_state.lives == starting_lives - 1
    assert app.state == AppState.PLAYING


def test_timeout_preserves_score_and_level() -> None:
    """Verify that timeout restarts the same level without losing score."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    assert app.game_state is not None
    app.game_state.score = 500
    original_level = app.active_level
    app._finish_timeout()
    assert app.game_state.score == 500
    assert app.game_state.current_level == 1
    assert app.active_level is not original_level


def test_timeout_on_last_life_ends_game() -> None:
    """Verify that losing the final life ends the game."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    assert app.game_state is not None
    original_level = app.active_level
    app.game_state.lives = 1
    app._finish_timeout()
    assert app.game_state.lives == 0
    assert app.state == AppState.GAME_OVER
    assert app.active_level is original_level


def test_timeout_waits_three_seconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that timeout waits three seconds before deducting a life."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    assert app.game_state is not None
    starting_lives = app.game_state.lives
    app.timeout_started_at = 10.0
    app.change_state(AppState.TIMEOUT)
    timestamps = iter([10.0, 12.9, 13.0])
    fake_time = SimpleNamespace(
        monotonic=lambda: next(timestamps),
        time=lambda: 0.0,
        sleep=lambda seconds: None,
    )
    monkeypatch.setattr(application_module, "time", fake_time)
    monkeypatch.setattr(app, "_load_bg", lambda: None)
    monkeypatch.setattr(app, "_run_game", lambda: None)
    monkeypatch.setattr(application_module.pg.display, "flip", lambda: None)
    frames = 0

    def simulate_events() -> None:
        """Check the delay, then stop after the second frame."""
        nonlocal frames
        frames += 1
        if frames == 2:
            assert app.state == AppState.TIMEOUT
            assert app.game_state is not None
            assert app.game_state.lives == starting_lives
            app.stop()

    monkeypatch.setattr(app, "_get_events", simulate_events)
    app.run()
    assert app.game_state.lives == starting_lives - 1
    assert app.state == AppState.PLAYING
    assert app.timeout_started_at is None


def test_new_game_resets_cheats() -> None:
    """Verify that a new game resets cheat settings and history."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    app.cheat_mode.toggle_invincibility()
    app.cheat_mode.toggle_disco_enabled()
    assert app.cheat_mode.invincible is True
    assert app.cheat_mode.disco_enabled is True
    assert app.cheat_mode.cheats_used is True
    _start_test_game(app)
    assert app.cheat_mode.invincible is False
    assert app.cheat_mode.disco_enabled is False
    assert app.cheat_mode.cheats_used is False
    assert app.cheat_mode.being_fabulous is False


def test_invincibility_prevents_life_loss() -> None:
    """Verify that invincibility protects against enraged ghosts."""
    app = create_collision_test_app([GhostState.ENRAGED])
    # Enable invincibility on the fully initialized test helper.
    app.cheat_mode.toggle_invincibility()
    assert app.game_state is not None
    starting_lives = app.game_state.lives
    app.resolve_ghost_collisions()
    assert app.game_state.lives == starting_lives
    assert app.state == AppState.PLAYING
