
"""Prepare a frozen greyscale background for Game Over."""

import numpy as np
import pygame as pg


def create_greyscale_background(
    original: pg.Surface,
) -> pg.Surface:
    """Return a darkened greyscale copy of a gameplay frame."""
    background = original.copy()

    # Read the image colours into a numerical pixel array.
    pixels = pg.surfarray.array3d(original).astype(np.uint16)

    # Calculate average brightness without Python pixel loops.
    brightness = (
        pixels[:, :, 0]
        + pixels[:, :, 1]
        + pixels[:, :, 2]
    ) // 3

    # Darken the greyscale image to 65% brightness.
    grey = (brightness * 65 // 100).astype(np.uint8)

    # Write the new colours while retaining the surface format.
    result_pixels = pg.surfarray.pixels3d(background)
    result_pixels[:, :, 0] = grey
    result_pixels[:, :, 1] = grey
    result_pixels[:, :, 2] = grey
    del result_pixels

    return background
