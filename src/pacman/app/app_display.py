
"""Own display surfaces, menus and visual assets."""

import os
import re
import sys
from collections.abc import Iterator

import pygame as pg

from pacman.app.actions import CharacterSelect, MainMenu
from pacman.app.actions import IMAGES, load_trans_image
from pacman.app.disco_effects import DiscoEffects
from pacman.app.hud import GameHUD
from pacman.app.viewport import GAME_HEIGHT, GAME_WIDTH
from pacman.app.viewport import MENU_HEIGHT, MENU_WIDTH


class AppDisplay:
    """Own the application's display resources and visual UI."""

    def __init__(self) -> None:
        """Create the display, menus and shared visual resources."""

        # Pygbag manages the browser canvas independently of the monitor.
        # Fullscreen mode could disrupt the browser's canvas dimensions.
        if sys.platform == "emscripten":
            self.screen = pg.display.set_mode((1280, 720))
        else:
            # Preserve the existing fullscreen behavior on desktop.
            self.screen = pg.display.set_mode(flags=pg.FULLSCREEN)

        # Gameplay and menus use separate logical canvas dimensions.
        self.game_canvas = pg.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.menu_canvas = pg.Surface(
            (MENU_WIDTH, MENU_HEIGHT),
            pg.SRCALPHA,
        )

        # Initialize menus on the shared logical menu canvas.
        self.main_menu = MainMenu(self.menu_canvas)
        self.char_select = CharacterSelect(self.menu_canvas)

        # Initialize shared gameplay presentation components.
        self.hud = GameHUD()
        self.disco_effects = DiscoEffects()

        # Load the maze wall and level background artwork once.
        self.block = load_trans_image(
            f"{IMAGES}/level-block.gif"
        )
        self.level_bg = load_trans_image(
            f"{IMAGES}/level-bg.png"
        )

        # Prepare the font used for gameplay information.
        self.font = pg.font.Font(
            "src/pacman/app/assets/PressStart2P-Regular.ttf",
            40,
        )

        # Ignore macOS metadata and load only numbered GIF frames.
        background_path = "./src/pacman/app/images/bg-frames"
        filenames = background_frame_filenames(background_path)

        self.bg_files = len(filenames)
        if self.bg_files == 0:
            raise FileNotFoundError(
                f"No numbered background frames in {background_path}"
            )

        # Load background frames incrementally during the game loop.
        self.frame_gen = load_frames(background_path, filenames)
        self.bg: list[pg.Surface] = []


def background_frame_filenames(path: str) -> list[str]:
    """Return numbered GIF frames in their intended playback order."""

    # Only filenames such as frame_1.gif should be considered.
    # This excludes .DS_Store and other unrelated files.
    filenames = [
        name for name in os.listdir(path)
        if re.fullmatch(r"frame_[0-9]+\.gif", name)
    ]

    # Sort by frame number rather than alphabetical filename order.
    return sorted(
        filenames,
        key=lambda name: int(name[6:-4]),
    )


def load_frames(
    path: str,
    filenames: list[str] | None = None,
) -> Iterator[pg.Surface]:
    """Load validated background frames in numerical order."""

    # Find the valid frame filenames if they were not supplied.
    if filenames is None:
        filenames = background_frame_filenames(path)

    # Yield frames individually so loading can happen incrementally.
    for filename in filenames:
        yield pg.image.load(
            f"{path}/{filename}"
        ).convert()
