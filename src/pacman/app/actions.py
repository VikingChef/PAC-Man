#!/usr/bin/env python3
"""Shared application actions for Pac-Man."""

from enum import Enum, auto
from typing import Final
from types import TracebackType
import pygame as pg
import time
import os
from collections.abc import Iterator


IMAGES: Final = 'src/pacman/app/images'


class MainMenuAction(Enum):
    """Actions available from the Pac-Man main menu."""

    # Define the choices the UI can return to the orchestrator.
    START_GAME = auto()
    VIEW_HIGHSCORES = auto()
    SHOW_INSTRUCTIONS = auto()
    EXIT = auto()


"""NOTE DELETE LATER:
UNHOVERED HEIGHT: 300
UNHOVERED WIDTH: 405
HOVERED HEIGTH: 350
HOVERED WIDTH: 470
"""


class Button:
    """Button class generates button objects, like Start Game."""

    def __init__(self,
                 path: str,
                 hover_path: str,
                 pos: tuple[int, int] = (0, 0),
                 hover_offset: tuple[int, int] = (45, 30)) -> None:
        """Initialize a Button object.

        Args:
            path (str): file path to the image.
            hover_path (str): file path to the alternative for hoverring.
            pos (tuple[int, int]): position of the image in x, y.
        """
        self.button: pg.Surface = load_trans_image(f'{IMAGES}/{path}')
        self.hover_button: pg.Surface = load_trans_image(
            f'{IMAGES}/{hover_path}')
        self.pos: tuple[int, int] = pos
        self.x, self.y = self.pos
        self.width, self.height = (self.button.get_width(),
                                   self.button.get_height())
        self.clicked: bool = False
        self.hover_offset: tuple[int, int] = hover_offset

    @property
    def hover_pos(self) -> tuple[int, int]:
        return (self.pos[0] - self.hover_offset[0],
                self.pos[1] - self.hover_offset[1])

    def render_button(self, screen: pg.Surface) -> None:
        """Render a button in a pre-made screen.

        Args:
            screen (pg.Surface): screen created by pygame.
        """
        screen.blit(self.button, self.pos)

    def render_hover_button(self, screen: pg.Surface) -> None:
        """Render a button in a pre-made screen for
            when the mouse hovers on it.

        Args:
            screen (pg.Surface): screen created by pygame.
        """
        screen.blit(self.hover_button, self.hover_pos)

    def hovering(self, mx: int, my: int) -> bool:
        """Find if the mouse is hovering on a button.

        Args:
            mx (int): x position of the mouse
            my (int): y position of the mouse

        Returns:
            bool: True if the mouse is hovering the button.
        """
        return (self.pos[0] <= mx <= self.width + self.pos[0]
                and self.pos[1] <= my <= self.height + self.pos[1])


class MainMenu:
    def __init__(self, screen: pg.Surface) -> None:
        R_DIST_FROM_CNTR: Final = 25
        L_DIST_FROM_CNTR: Final = 430
        button_r: int = screen.get_width() // 2 + R_DIST_FROM_CNTR
        button_l: int = screen.get_width() // 2 - L_DIST_FROM_CNTR
        height: int = 400
        BTTN_W: Final = 450

        # Start Game settings
        self.start_game: Button = Button('start-game.png',
                                         'start-game-hover.png',
                                         pos=(button_l - BTTN_W, height))

        # High Scores settings
        self.high_scores: Button = Button('high-scores.png',
                                          'high-scores-hover.png',
                                          pos=(button_l, height))

        # Instructions settings
        self.instr: Button = Button('instructions.png',
                                    'instructions-hover.png',
                                    pos=(button_r, height))

        # Exit settings
        self.exit: Button = Button('sashay-away.png',
                                   'sashay-away-hover.png',
                                   pos=(button_r + BTTN_W, height))

        self.BUTTONS: Final = [self.start_game,
                               self.high_scores,
                               self.instr,
                               self.exit]

        # Title settings
        self.title: list[pg.Surface] = [
            load_trans_image(f'{IMAGES}/title_{i}.png') for i in range(1, 6)]
        title_width: int = center(screen.get_width(),
                                  self.title[0].get_width())
        self.title_pos: tuple[int, int] = (title_width, 100)

    def render_main_menu(self,
                         start_time: float,
                         mouse: tuple[int, int],
                         screen: pg.Surface) -> None:
        now: float = time.time() * 1000
        mx, my = mouse
        title_frame: int = (
            (int(now - start_time) // 125)
            % len(self.title)
            )
        screen.blit(self.title[title_frame],
                    self.title_pos)

        # render buttons
        for button in self.BUTTONS:
            if button.hovering(mx, my):
                button.render_hover_button(screen)
            else:
                button.render_button(screen)

        for event in pg.event.get():
            for button in self.BUTTONS:
                if (event.type == pg.MOUSEBUTTONDOWN
                   and button.hovering(mx, my)):
                    button.clicked = True
                    if button == self.exit:
                        self.running = False


class CharacterSelect:
    def __init__(self, screen: pg.Surface):
        self.queen_1: Button = Button('queen-1.png',
                                      'queen-1-hover.png')
        x: int = center(screen.get_width() / 2, self.queen_1.button.get_width())
        y: int = 200
        self.queen_1.pos = (x, y)
        self.queen_2: Button = Button('queen-2.png',
                                      'queen-2-hover.png',
                                      hover_offset=(10, 30))
        x = int(
            screen.get_width() / 4 * 3
            - self.queen_2.button.get_width() / 2
            )
        y = (self.queen_1.button.get_height() -
             self.queen_2.button.get_height() + y + 1)
        self.queen_2.pos = (x, y)
        self.QUEENS: Final = [self.queen_1, self.queen_2]

        # Choose your diva and Queen Names
        self.choose: pg.Surface = load_trans_image(
            f'{IMAGES}/select-your-diva.png')
        self.waka: pg.Surface = load_trans_image(
            f'{IMAGES}/waka-waka-wanda.png')
        self.ms_pellet: pg.Surface = load_trans_image(
            f'{IMAGES}/ms-power-pellet.png')

        choose_x: int = center(screen.get_width(), self.choose.get_width())
        self.choose_pos: tuple[int, int] = (choose_x, 100)

        waka_x: int = self.queen_1.pos[0] + self.queen_1.width + 10
        self.waka_pos: tuple[int, int] = (waka_x,
                                          self.queen_1.pos[1] + 250)

        ms_pellet_x: int = (self.queen_2.pos[0]
                            - self.ms_pellet.get_width()) - 10
        ms_pellet_y: int = self.queen_2.height + self.queen_2.pos[1] - 75
        self.ms_pellet_pos: tuple[int, int] = (ms_pellet_x,
                                               ms_pellet_y)

    def render_char_select(self,
                           mouse: tuple[int, int],
                           screen: pg.Surface) -> None:
        mx, my = mouse
        for queen in self.QUEENS:
            if queen.hovering(mx, my):
                queen.render_hover_button(screen)
            else:
                queen.render_button(screen)
            screen.blit(self.choose, self.choose_pos)
            screen.blit(self.waka, self.waka_pos)
            screen.blit(self.ms_pellet, self.ms_pellet_pos)

        for event in pg.event.get():
            for queen in self.QUEENS:
                if (event.type == pg.MOUSEBUTTONDOWN
                   and queen.hovering(mx, my)):
                    queen.clicked = True


class LoadingBar:
    def __init__(self, screen: pg.Surface) -> None:
        path: str = f'{IMAGES}/loading-frames'
        self.frames: list[pg.Surface] = [
            load_trans_image(f'{path}/frame_{i}.png') for i in range(5)
            ]
        x: int = center(screen.get_width(), self.frames[0].get_width())
        y: int = center(screen.get_height(), self.frames[0].get_height())
        self.frame_pos: tuple[int, int] = (x, y)
        self.text: pg.Surface = load_trans_image(f'{IMAGES}/loading.png')
        x = center(screen.get_width(), self.text.get_width())
        y += self.frames[0].get_height() + 10
        self.text_pos: tuple[int, int] = (x, y)
        self.screen: pg.Surface = screen

    def render_bar(self, frame: int) -> None:
        self.screen.blit(self.frames[frame], self.frame_pos)
        self.screen.blit(self.text, self.text_pos)


class UI:
    """Main Page for UI"""

    def __init__(self) -> None:
        """Initialize a UI object."""
        self.screen: pg.Surface = pg.display.set_mode(flags=pg.FULLSCREEN)
        self.running: bool = True

        # Background
        path: str = './src/pacman/app/images/bg-frames'
        self.bg_files: int = len(os.listdir(path))
        self.frame_gen: Iterator[pg.Surface] = load_frames(path)
        self.bg: list[pg.Surface] = []

        self.main_menu: MainMenu = MainMenu(self.screen)

        self.char_select: CharacterSelect = CharacterSelect(self.screen)

        self.loading: LoadingBar = LoadingBar(self.screen)

    @property
    def bg_pos(self) -> tuple[int, int]:
        if self.bg == []:
            return (0, 0)
        else:
            bg_x: int = center(self.screen.get_width(),
                               self.bg[0].get_width())
            bg_y: int = center(self.screen.get_height(),
                               self.bg[0].get_height())
            return (bg_x, bg_y)

    def render(self) -> None:
        """Render main menu"""

        start_time: float = time.time() * 1000
        while self.running:
            iter_start: float = time.time()
            frame: pg.Surface = next(self.frame_gen, None)
            if frame is not None:
                self.bg.append(frame)
                self.loading.render_bar(
                    min(4, len(self.bg) * 5 // self.bg_files))
            else:
                mx, my = pg.mouse.get_pos()

                # tracking events such as quitting the program
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False

                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            self.running = False

                now: float = time.time() * 1000
                bg_frame: int = (int(now - start_time) // 100) % len(self.bg)
                self.screen.blit(self.bg[bg_frame], self.bg_pos)

                if not self.main_menu.start_game.clicked:
                    self.main_menu.render_main_menu(start_time,
                                                    (mx, my),
                                                    self.screen)
                else:
                    self.char_select.render_char_select((mx, my), self.screen)

            pg.display.flip()
            iter_end: float = time.time()
            time.sleep(max(0, 1 / 60 - (iter_end - iter_start)))

    def _test_actions(self) -> None:
        """Test actions until there is proper actions in-place."""
        print("High Scores clicked." if self.main_menu.high_scores.clicked
              else "High Scores not clicked.")
        print("Instructions were shown." if self.main_menu.instr.clicked
              else "Instructions were not shown.")
        print("Waka Waka Wanda was chosen." if self.char_select.queen_1.clicked
              else "Waka Waka Wanda wasn't chosen.")
        print("Ms. Power Pellet was chosen." if self.
              char_select.queen_2.clicked
              else "Ms. Power Pellet wasn't chosen.")

    def __enter__(self) -> 'UI':
        """Dunder method for context managers.

        Returns:
            Visualizer: Visualizer object"""
        return self

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: TracebackType | None) -> None:
        """Dunder method for context managers.

        Args:
            exc_type (type[BaseException] | None): Class of the exception
                raised inside the ``with`` block, or None if it exited
                normally.
            exc (BaseException | None): The exception instance, or None.
            tb (TracebackType | None): Traceback of the exception, or None.
        """
        pg.quit()


def load_trans_image(path: str) -> pg.Surface:
    return pg.image.load(path).convert_alpha()


def center(screen_dim: int, item_dim: int) -> int:
    return int(screen_dim / 2 - item_dim / 2)


def load_frames(path: str) -> Iterator[pg.Surface]:
    dir_list: list[str] = sorted(
            os.listdir(path),
            key=lambda x: int(x[x.find('_') + 1:x.find('.')])
            )
    for frame in dir_list:
        yield pg.image.load(f'{path}/{frame}').convert()


def start_UI() -> None:
    """Main function for starting the UI."""

    with UI() as ui:
        ui.render()
        ui._test_actions()


if __name__ == "__main__":
    start_UI()
