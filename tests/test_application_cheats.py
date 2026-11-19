"""Test application cheats and score handling."""

from types import SimpleNamespace
import pytest
import pygame as pg
from pacman.app.application import AppState, PacManApp
from pacman.game.ghost import GhostState
from pacman.app import application as application_module
from tests.app_test_helpers import (
    _test_config,
    _start_test_game,
    create_collision_test_app,
)


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


def test_disco_mode_doubles_points() -> None:
    """Verify disco mode doubles points without marking cheats as used."""

    app = PacManApp(_test_config())
    _start_test_game(app)

    assert app.game_state is not None

    # Normal scoring.
    app.award_points(10)
    assert app.game_state.score == 10

    # Disco mode doubles points.
    app.cheat_mode.toggle_disco_enabled()
    app.award_points(10)
    assert app.game_state.score == 30

    # Disco mode does not count as cheating.
    assert app.cheat_mode.cheats_used is False

    # Disabling disco restores normal scoring.
    app.cheat_mode.toggle_disco_enabled()
    app.award_points(10)
    assert app.game_state.score == 40


def test_timer_freeze_preserves_ghost_lifecycle() -> None:
    """Freeze level time while frightened and respawn timers continue."""

    app = PacManApp(_test_config())
    _start_test_game(app)

    assert app.active_level is not None
    level = app.active_level

    level.frighten_ghosts()

    ghost = level.ghosts[0]
    assert ghost.eat() is True

    # Five seconds pass with the level countdown frozen.
    level.tick(5, freeze_level_timer=True)

    # The level countdown has not changed.
    assert level.remaining_time == 90

    # Frightened time continues to decrease.
    assert level.frightened_timer == 1

    # The eaten ghost has completed its five-second respawn.
    assert ghost.respawn_timer == 0
    assert ghost.position == ghost.spawn_position

    # Frightened mode is still active, so the ghost respawns frightened.
    assert ghost.state == GhostState.FRIGHTENED

    # Normal countdown behaviour resumes when the freeze is disabled.
    level.tick(1)

    assert level.remaining_time == 89
    assert level.frightened_timer == 0
    assert ghost.state == GhostState.ENRAGED


def test_ghost_freeze_stops_movement_not_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Frozen ghosts do not move, but the level timer continues."""

    app = PacManApp(_test_config())
    _start_test_game(app)

    assert app.active_level is not None
    level = app.active_level

    app.cheat_mode.toggle_ghost_freeze()

    movement_calls = 0

    def track_ghost_movement() -> None:
        nonlocal movement_calls
        movement_calls += 1

    monkeypatch.setattr(level, "move_ghosts", track_ghost_movement)

    # Simulate enough time for ghost movement and one timer tick.
    timestamps = iter([0.0, 1.1])

    fake_time = SimpleNamespace(
        monotonic=lambda: next(timestamps),
        time=lambda: 0.0,
        sleep=lambda seconds: None,
    )

    monkeypatch.setattr(application_module, "time", fake_time)
    monkeypatch.setattr(app, "_load_bg", lambda: None)
    monkeypatch.setattr(app, "_get_events", lambda: None)
    monkeypatch.setattr(
        application_module.pg.display,
        "flip",
        lambda: None,
    )
    monkeypatch.setattr(app, "_run_game", app.stop)

    app.run()

    assert movement_calls == 0
    assert level.remaining_time == 89


def test_cheat_keyboard_shortcuts_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify old keyboard shortcuts no longer activate cheats."""

    app = PacManApp(_test_config())
    _start_test_game(app)

    shortcuts = [
        (pg.K_f, "disco_enabled"),
        (pg.K_i, "invincible"),
        (pg.K_g, "ghosts_frozen"),
        (pg.K_t, "timer_stopped"),
    ]

    for key, attribute in shortcuts:
        event = pg.event.Event(pg.KEYDOWN, key=key)
        monkeypatch.setattr(pg.event, "get", lambda: [event])

        # Old shortcuts must not activate cheats.
        app._get_events()
        assert getattr(app.cheat_mode, attribute) is False


def test_cheating_permanently_disables_scoring() -> None:
    """Cheating resets points and prevents further scoring."""
    app = PacManApp(_test_config())
    _start_test_game(app)

    assert app.game_state is not None

    # Earn points normally before activating a cheat.
    app.award_points(100)
    assert app.game_state.score == 100

    # Invincibility invalidates the score immediately.
    app.cheat_mode.toggle_invincibility()
    assert app.game_state.score == 0

    # No further points may be awarded while cheating.
    app.award_points(50)
    assert app.game_state.score == 0

    # Disabling invincibility does not restore scoring.
    app.cheat_mode.toggle_invincibility()
    app.award_points(50)
    assert app.game_state.score == 0

    # Disco Mode cannot override the permanent scoring lockout.
    app.cheat_mode.toggle_disco_enabled()
    app.award_points(50)
    assert app.game_state.score == 0
