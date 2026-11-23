"""Shared image loading and positioning helpers for the interface."""

from typing import Final

import pygame as pg


IMAGES: Final = "src/pacman/app/images"


def load_trans_image(path: str) -> pg.Surface:
    """Load a transparent image

    Args:
        path (str): path to the image

    Returns:
        pg.Surface: The image as a pygame object
    """
    return pg.image.load(path).convert_alpha()


def center(src_dim: int, dest_dim: int) -> int:
    """Center an image according to another surface.

    Args:
        screen_dim (int): dimension of one of the objects
        item_dim (int): dimension of the other object

    Returns:
        int: position for the centered object.
    """
    return int(src_dim / 2 - dest_dim / 2)
