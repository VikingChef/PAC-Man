
"""Own display surfaces, menus and visual assets."""

import os
import re
from collections.abc import Iterator

import pygame as pg

from pacman.app.actions import CharacterSelect, LoadingBar, MainMenu
from pacman.app.actions import IMAGES, load_trans_image
from pacman.app.disco_effects import DiscoEffects
from pacman.app.hud import GameHUD
from pacman.app.viewport import GAME_HEIGHT, GAME_WIDTH
from pacman.app.viewport import MENU_HEIGHT, MENU_WIDTH


class AppDisplay:
    """Own the application's display resources and visual UI."""

    def __init__(self) -> None:
        """Create the display, menus and shared visual resources."""
        # The physical display uses the monitor's resolution.
        self.screen = pg.display.set_mode(flags=pg.FULLSCREEN)

        # Gameplay and menus have independent logical dimensions.
        self.game_canvas = pg.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.menu_canvas = pg.Surface(
            (MENU_WIDTH, MENU_HEIGHT),
            pg.SRCALPHA,
        )

        # UI components share their owning display resources.
        self.main_menu = MainMenu(self.menu_canvas)
        self.char_select = CharacterSelect(self.menu_canvas)
        self.loading = LoadingBar(self.screen)
        self.hud = GameHUD()
        self.disco_effects = DiscoEffects()

        # Shared maze and background artwork.
        self.block = load_trans_image(
            f"{IMAGES}/level-block.gif"
        )
        self.level_bg = load_trans_image(
            f"{IMAGES}/level-bg.png"
        )

        self.font = pg.font.Font(
            "src/pacman/app/assets/PressStart2P-Regular.ttf",
            40,
        )

        # Load only numbered GIF frames, ignoring macOS metadata files.
        background_path = "./src/pacman/app/images/bg-frames"
        filenames = background_frame_filenames(background_path)
        self.bg_files = len(filenames)
        if self.bg_files == 0:
            raise FileNotFoundError(
                f"No numbered background frames in {background_path}"
            )
        self.frame_gen = load_frames(background_path, filenames)
        self.bg: list[pg.Surface] = []


def background_frame_filenames(path: str) -> list[str]:
    """Return numbered GIF frames in their intended playback order."""
    # A .DS_Store file must never reach the integer frame-number parser.
    filenames = [
        name for name in os.listdir(path)
        if re.fullmatch(r"frame_[0-9]+\.gif", name)
    ]
    return sorted(
        filenames,
        key=lambda name: int(name[6:-4]),
    )


def load_frames(
    path: str,
    filenames: list[str] | None = None,
) -> Iterator[pg.Surface]:
    """Load validated background frames in numerical order."""
    if filenames is None:
        filenames = background_frame_filenames(path)

    for filename in filenames:
        yield pg.image.load(
            f"{path}/{filename}"
        ).convert()
