"""Backwards-compatible public interface for application UI actions."""

import os
from collections.abc import Iterator

import pygame as pg

from pacman.app.character_select import CharacterSelect
from pacman.app.main_menu import MainMenu
from pacman.app.menu_actions import CharSelectAction, MainMenuAction
from pacman.app.ui_assets import IMAGES, center, load_trans_image
from pacman.app.ui_button import Button


# Preserve existing imports while the UI classes live in focused modules.
__all__ = [
    "Button",
    "CharSelectAction",
    "CharacterSelect",
    "IMAGES",
    "MainMenu",
    "MainMenuAction",
    "UI",
    "center",
    "load_frames",
    "load_trans_image",
]


class UI:
    """Main Page for UI"""

    def __init__(self) -> None:
        """Initialize a UI object."""

        self.screen: pg.Surface = pg.display.set_mode(
            flags=pg.FULLSCREEN
        )
        self.running: bool = True

        # Background
        path: str = './src/pacman/app/images/bg-frames'
        self.bg_files: int = len(os.listdir(path))
        self.frame_gen: Iterator[pg.Surface] = load_frames(path)
        self.bg: list[pg.Surface] = []

        self.main_menu: MainMenu = MainMenu(self.screen)
        self.char_select: CharacterSelect = CharacterSelect(self.screen)

    @property
    def bg_pos(self) -> tuple[int, int]:
        """Return the background position for the current screen size."""
        if self.bg == []:
            return (0, 0)
        else:
            bg_x: int = center(
                self.screen.get_width(),
                self.bg[0].get_width(),
            )
            bg_y: int = center(
                self.screen.get_height(),
                self.bg[0].get_height(),
            )
            return (bg_x, bg_y)


def load_frames(path: str) -> Iterator[pg.Surface]:
    """Load animation frames in numerical order, one at a time."""
    dir_list: list[str] = sorted(
        os.listdir(path),
        key=lambda x: int(
            x[x.find('_') + 1:x.find('.')]
        ),
    )

    for frame in dir_list:
        yield pg.image.load(
            f'{path}/{frame}'
        ).convert()
