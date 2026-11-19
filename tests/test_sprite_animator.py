"""Tests for sprite interpolation independent of gameplay movement."""

import pygame as pg
import pytest

from pacman.app import sprite_animator
from pacman.app.sprite_animator import SpriteAnimator


def _animator() -> SpriteAnimator:
    """Build an animator with a predictable visual maze."""
    animator = SpriteAnimator(pg.Surface((16, 16)))
    positions = [
        [(column * 16, row * 16) for column in range(5)]
        for row in range(5)
    ]
    animator.reset(positions)
    return animator


def test_player_interpolates_without_changing_logical_position(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Check that halfway movement only changes drawing coordinates."""
    animator = _animator()
    animator.start_player_move((0, 0), (1, 0), 10.0)
    monkeypatch.setattr(sprite_animator.time, "monotonic", lambda: 10.06)

    assert animator.position((1, 0), (8, 8)) == (36, 20)
    assert animator.player_end == (1, 0)


def test_player_animation_clears_after_completion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Check that finished interpolation no longer needs tracking."""
    animator = _animator()
    animator.start_player_move((0, 0), (1, 0), 10.0)
    monkeypatch.setattr(sprite_animator.time, "monotonic", lambda: 11.0)

    assert animator.position((1, 0), (8, 8)) == (52, 20)
    assert animator.player_start is None
    assert animator.player_end is None


def test_reset_clears_movements_and_replaces_geometry() -> None:
    """Check level transitions clear animation without stale positions."""
    animator = _animator()
    animator.start_player_move((0, 0), (1, 0), 10.0)
    new_positions = [[(5, 6) for _ in range(3)] for _ in range(3)]

    animator.reset(new_positions)

    assert animator.player_start is None
    assert animator.player_end is None
    assert animator.ghost_moves == {}
    assert animator.position((0, 0), (8, 8)) == (9, 10)
