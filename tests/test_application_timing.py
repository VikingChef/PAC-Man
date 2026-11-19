"""Test application timing, pause handling and timeouts."""

from types import SimpleNamespace
import pytest
from pacman.app.application import AppState, PacManApp
from pacman.app import application as application_module
from tests.app_test_helpers import _test_config, _start_test_game


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
