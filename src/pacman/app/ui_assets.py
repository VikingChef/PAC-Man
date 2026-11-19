"""Shared image loading and positioning helpers for the interface."""

from typing import Final

import pygame as pg


IMAGES: Final = "src/pacman/app/images"


def load_trans_image(path: str) -> pg.Surface:
    return pg.image.load(path).convert_alpha()


def center(screen_dim: int, item_dim: int) -> int:
    return int(screen_dim / 2 - item_dim / 2)
