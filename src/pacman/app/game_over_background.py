
"""Prepare a frozen greyscale background for the Game Over screen."""

import pygame as pg


def create_greyscale_background(
    original: pg.Surface,
) -> pg.Surface:
    """Return a darkened greyscale copy of a gameplay frame."""
    background = original.copy()
    width, height = background.get_size()

    # Modify individual image pixels, preserving their original alpha.
    # This avoids relying on specialised Pygame colour filters.
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = background.get_at((x, y))

            # Average the colour channels and darken the result.
            brightness = (red + green + blue) // 3
            grey = brightness * 65 // 100

            background.set_at(
                (x, y),
                (grey, grey, grey, alpha),
            )

    return background
