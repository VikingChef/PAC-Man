
"""Resize image buffers using nearest-neighbour pixel sampling."""

import numpy as np
import pygame as pg


def scale_pixels(
    source: pg.Surface,
    target_size: tuple[int, int],
) -> pg.Surface:
    """Copy source pixels into a resized image buffer."""
    source_width, source_height = source.get_size()
    target_width, target_height = target_size

    if min(source_width, source_height) <= 0:
        raise ValueError("Source dimensions must be positive.")

    if min(target_width, target_height) <= 0:
        raise ValueError("Target dimensions must be positive.")

    if source.get_bitsize() != 32:
        raise ValueError("Pixel scaling requires a 32-bit surface.")

    # Preserve the source pixel format, including its alpha mask.
    target = pg.Surface(
        target_size,
        flags=source.get_flags() & pg.SRCALPHA,
        depth=32,
        masks=source.get_masks(),
    )

    # Map each target pixel to its corresponding source pixel.
    source_x = (
        np.arange(target_width, dtype=np.int64)
        * source_width // target_width
    )
    source_y = (
        np.arange(target_height, dtype=np.int64)
        * source_height // target_height
    )

    # Read and write the actual image buffers, not a graphics
    # library's built-in image transformation operation.
    source_pixels = pg.surfarray.array2d(source)
    target_pixels = pg.surfarray.pixels2d(target)

    target_pixels[:, :] = source_pixels[
        source_x[:, None],
        source_y[None, :],
    ]

    # Release the locked target buffer before returning it.
    del target_pixels

    return target
