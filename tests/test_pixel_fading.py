
"""Test direct pixel-buffer colour blending."""

import pytest
import pygame as pg

from pacman.app.pixel_fading import blend_pixels


def test_blend_at_zero_preserves_original() -> None:
    """Zero progress must preserve the original colour."""
    original = pg.Surface((1, 1), depth=32)
    target = pg.Surface((1, 1), depth=32)

    original.fill((200, 100, 50))
    target.fill((0, 0, 0))

    result = blend_pixels(original, target, 0.0)

    assert result.get_at((0, 0))[:3] == (200, 100, 50)


def test_blend_at_one_uses_target() -> None:
    """Full progress must produce the target colour."""
    original = pg.Surface((1, 1), depth=32)
    target = pg.Surface((1, 1), depth=32)

    original.fill((200, 100, 50))
    target.fill((0, 0, 0))

    result = blend_pixels(original, target, 1.0)

    assert result.get_at((0, 0))[:3] == (0, 0, 0)


def test_blend_halfway_mixes_colours() -> None:
    """Halfway progress must mix both colour values."""
    original = pg.Surface((1, 1), depth=32)
    target = pg.Surface((1, 1), depth=32)

    original.fill((0, 0, 0))
    target.fill((200, 100, 50))

    result = blend_pixels(original, target, 0.5)
    red, green, blue, _ = result.get_at((0, 0))

    assert abs(red - 100) <= 1
    assert abs(green - 50) <= 1
    assert abs(blue - 25) <= 1


def test_blend_preserves_original_alpha() -> None:
    """Blending colours must retain original transparency."""
    original = pg.Surface((1, 1), pg.SRCALPHA, 32)
    target = pg.Surface((1, 1), pg.SRCALPHA, 32)

    original.fill((200, 100, 50, 128))
    target.fill((0, 0, 0, 255))

    result = blend_pixels(original, target, 0.5)

    assert result.get_at((0, 0)).a == 128
    assert original.get_at((0, 0)).a == 128


def test_blend_rejects_different_image_sizes() -> None:
    """Images of different dimensions cannot be blended."""
    original = pg.Surface((2, 2))
    target = pg.Surface((3, 3))

    with pytest.raises(ValueError):
        blend_pixels(original, target, 0.5)


def test_blend_rejects_invalid_progress() -> None:
    """Blend progress must remain between zero and one."""
    original = pg.Surface((1, 1))
    target = pg.Surface((1, 1))

    with pytest.raises(ValueError):
        blend_pixels(original, target, 1.5)
