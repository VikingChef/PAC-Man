
"""Test responsive canvas scaling and maze positioning."""

import pygame as pg

from pacman.app.viewport import (
    fit_canvas,
    maze_origin,
    render_canvas,
    screen_to_canvas,
)


def test_fit_canvas() -> None:
    """Verify scaling preserves proportions and centres the canvas."""

    # The display is wider than the square game canvas.
    # Height must limit the scale to prevent vertical clipping.
    scale, position = fit_canvas((1000, 1000), (1600, 900))

    assert scale == 0.9
    assert position == (350, 0)


def test_maze_origin() -> None:
    """Verify the maze is centred below the reserved HUD."""

    # A 15x15 maze expands to 31x31 blocks of 35 pixels each.
    # The HUD must not overlap the resulting 1085x1085 maze.
    position = maze_origin((1085, 1085))

    assert position == (417, 237)


def test_render_canvas() -> None:
    """Verify the canvas scales and unused margins are cleared."""

    # Use an off-screen display so the test opens no game window.
    canvas = pg.Surface((100, 100))
    display = pg.Surface((200, 100))

    canvas.fill((255, 0, 0))
    render_canvas(canvas, display)

    # The original red image should occupy the centre.
    assert display.get_at((100, 50))[:3] == (255, 0, 0)

    # Empty margins must use our chosen background colour.
    assert display.get_at((0, 0))[:3] == (24, 18, 38)


def test_screen_to_canvas() -> None:
    """Verify mouse clicks map to logical canvas coordinates."""

    # A square canvas is scaled to 90% and centred horizontally.
    canvas_size = (1000, 1000)
    display_size = (1600, 900)

    # The physical centre must map to the canvas centre.
    position = screen_to_canvas(
        (800, 450),
        canvas_size,
        display_size,
    )
    assert position == (500, 500)

    # Clicks outside the scaled canvas must be ignored.
    position = screen_to_canvas(
        (100, 450),
        canvas_size,
        display_size,
    )
    assert position is None
