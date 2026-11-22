
"""Blend image colours using direct pixel-buffer operations."""

import numpy as np
import pygame as pg


def blend_pixels(
    original: pg.Surface,
    target: pg.Surface,
    progress: float,
) -> pg.Surface:
    """Blend between two images while preserving transparency."""
    if original.get_size() != target.get_size():
        raise ValueError("Both images must have identical dimensions.")

    if not 0.0 <= progress <= 1.0:
        raise ValueError("Blend progress must be between 0 and 1.")

    # Copy the original image so its format and alpha are preserved.
    result = original.copy()

    # Read the RGB channels without changing either source image.
    original_pixels = pg.surfarray.array3d(original)
    target_pixels = pg.surfarray.array3d(target)

    # Integer arithmetic avoids rounding errors from float colours.
    strength = round(progress * 255)
    original_weight = 255 - strength

    blended = (
        original_pixels.astype(np.uint32) * original_weight
        + target_pixels.astype(np.uint32) * strength
        + 127
    ) // 255

    # Write the calculated colours to the result image buffer.
    result_pixels = pg.surfarray.pixels3d(result)
    result_pixels[:, :, :] = blended.astype(np.uint8)
    del result_pixels

    return result
