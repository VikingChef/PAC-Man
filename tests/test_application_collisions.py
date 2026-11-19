
"""Test application ghost collisions and life loss."""

from pathlib import Path
from types import SimpleNamespace

import pygame as pg
import pytest

from pacman.app import application as application_module
from pacman.app.application import AppState, PacManApp
from pacman.game.ghost import GhostState
from pacman.game.highscores import HighScoreManager
from pacman.game.pacgum import PacgumType
from pacman.game.run_finalizer import RunFinalizer
from pacman.maze.direction import Direction
from tests.app_test_helpers import (
    _start_test_game,
    _test_config,
    create_collision_test_app,
)


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
    """An enraged ghost starts death without awarding ghost points."""
    app = create_collision_test_app([
        GhostState.ENRAGED,
        GhostState.FRIGHTENED,
    ])

    assert app.game_state is not None
    assert app.active_level is not None

    app.resolve_ghost_collisions()

    # The collision is detected, but the death scene comes first.
    assert app.state == AppState.DYING
    assert app.game_state.lives == 3
    assert app.game_state.score == 0
    assert app.death_started_at is not None

    # Only after the scene finishes is the life deducted.
    app._finish_death()

    assert app.game_state.lives == 2
    assert app.state == AppState.PLAYING
    assert app.death_started_at is None

    # Respawning restores the ghosts to their normal state.
    for ghost in app.active_level.ghosts:
        assert ghost.state == GhostState.ENRAGED


def test_final_life_collision_ends_game(tmp_path: Path) -> None:
    """The final life ends only after the visible death transition."""
    app = create_collision_test_app(
        [GhostState.ENRAGED],
        lives=1,
    )

    # This lightweight test fixture needs the new run finalizer.
    manager = HighScoreManager(str(tmp_path / "scores.json"))
    app.run_finalizer = RunFinalizer(manager)
    app.run_finalizer.start_run()

    assert app.game_state is not None

    app.resolve_ghost_collisions()

    # A fatal collision must first enter the death transition.
    assert app.state == AppState.DYING
    assert app.game_state.lives == 1

    app._finish_death()

    assert app.game_state.lives == 0
    assert app.state == AppState.GAME_OVER
    assert app.death_started_at is None
    assert app.run_finalizer.run_finalized is True


def test_player_movement_into_enraged_ghost_loses_life() -> None:
    """Moving into a ghost shows the collision before life loss."""
    app = PacManApp(_test_config())
    _start_test_game(app)

    assert app.active_level is not None
    assert app.game_state is not None

    level = app.active_level
    player = level.player
    ghost = level.ghosts[0]

    # Find an accessible adjacent cell for the ghost.
    direction = next(
        direction for direction in Direction
        if level.maze.can_move(player.position, direction)
    )

    dx, dy = direction.value
    x, y = player.position
    destination = (x + dx, y + dy)

    ghost.position = destination
    ghost.state = GhostState.ENRAGED

    # A normal pacgum must not frighten the ghost on contact.
    level.pacgums[destination] = (
        PacgumType.PACGUM,
        pg.Surface((1, 1)),
    )

    moved = app.move_player(direction)

    assert moved is True

    # Both characters occupy the collision cell before respawning.
    assert player.position == destination
    assert ghost.position == destination
    assert app.state == AppState.DYING
    assert app.game_state.lives == 3

    # Finish the transition and verify the reset.
    app._finish_death()

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

    # The super-pacgum must be collected before ghost collision.
    ghost.position = destination
    ghost.state = GhostState.ENRAGED
    level.pacgums[destination] = (
        PacgumType.SUPER_PACGUM,
        pg.Surface((1, 1)),
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


def test_ghost_movement_collision_loses_one_life(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify a ghost collision stops movement before life loss."""
    app = PacManApp(_test_config())
    _start_test_game(app)

    assert app.active_level is not None
    assert app.game_state is not None

    level = app.active_level
    ghost = level.ghosts[0]
    player = level.player
    movement_calls = 0

    def simulate_ghost_movement() -> None:
        """Simulate a ghost reaching the player's position."""
        nonlocal movement_calls
        movement_calls += 1
        ghost.position = player.position

    monkeypatch.setattr(
        level,
        "move_ghosts",
        simulate_ghost_movement,
    )

    ghost_interval = level.config.ghost_move_interval_ms / 1000

    # The third reading records when the death transition begins.
    timestamps = iter([
        0.0,
        ghost_interval * 3 + 0.01,
        ghost_interval * 3 + 0.01,
    ])

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

    # One collision must stop further ghost movement.
    assert movement_calls == 1
    assert app.state == AppState.DYING
    assert app.game_state.lives == 3

    # Both characters must occupy the collision cell.
    assert ghost.position == player.position
    assert app.death_started_at is not None

    # Life loss happens after the visible collision.
    app._finish_death()

    assert app.game_state.lives == 2
    assert app.state == AppState.PLAYING
    assert app.death_started_at is None
    assert player.position == player.spawn_position
    assert ghost.position == ghost.spawn_position
