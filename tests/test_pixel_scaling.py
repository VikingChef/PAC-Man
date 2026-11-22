
"""Test nearest-neighbour image scaling."""

import pygame as pg

from pacman.app.pixel_scaling import scale_pixels


def test_scaling_preserves_pixel_colours() -> None:
    """Each source pixel should fill its corresponding area."""
    source = pg.Surface((2, 2), depth=32)
    source.set_at((0, 0), (255, 0, 0))
    source.set_at((1, 0), (0, 255, 0))
    source.set_at((0, 1), (0, 0, 255))
    source.set_at((1, 1), (255, 255, 0))

    result = scale_pixels(source, (4, 4))

    assert result.get_size() == (4, 4)
    assert result.get_at((0, 0))[:3] == (255, 0, 0)
    assert result.get_at((1, 1))[:3] == (255, 0, 0)
    assert result.get_at((2, 0))[:3] == (0, 255, 0)
    assert result.get_at((0, 2))[:3] == (0, 0, 255)
    assert result.get_at((3, 3))[:3] == (255, 255, 0)


def test_scaling_preserves_transparency() -> None:
    """Alpha values should survive resizing."""
    source = pg.Surface((2, 1), pg.SRCALPHA, 32)
    source.set_at((0, 0), (255, 0, 0, 128))
    source.set_at((1, 0), (0, 255, 0, 0))

    result = scale_pixels(source, (4, 2))

    assert result.get_at((0, 0)) == (255, 0, 0, 128)
    assert result.get_at((3, 1)) == (0, 255, 0, 0)
