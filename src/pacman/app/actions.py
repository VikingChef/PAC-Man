#!/usr/bin/env python3
"""Shared application actions for Pac-Man."""

from enum import Enum, auto
from typing import Final
from types import TracebackType
import pygame as pg
import time
import os


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
    IMAGES: Final = 'src/pacman/app/images'

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
        self.button: pg.Surface = (
            pg.image
              .load(f'{self.IMAGES}/{path}')
              .convert_alpha()
              )
        self.hover_button: pg.Surface = (
            pg.image
              .load(f'{self.IMAGES}/{hover_path}')
              .convert_alpha()
              )
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


class UI:
    """Main Page for UI"""

    def __init__(self) -> None:
        """Initialize a UI object."""
        self.screen: pg.Surface = pg.display.set_mode(flags=pg.FULLSCREEN)
        self.running: bool = True

        button_r: int = self.screen.get_width() // 2 + 25
        button_l: int = self.screen.get_width() // 2 - 430
        height: int = 400
        # Start Game settings
        self.start_game: Button = Button('start-game.png',
                                         'start-game-hover.png',
                                         pos=(button_l - 450, height))

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
                                   pos=(button_r + 450, height))

        self.BUTTONS: Final = [self.start_game,
                               self.high_scores,
                               self.instr,
                               self.exit]

        # Title settings
        self.title: list[pg.Surface] = [(
            pg.image
              .load(f'{self.exit.IMAGES}/title_{i}.png')
              .convert_alpha()
              ) for i in range(1, 6)]
        title_width: int = int(
            self.screen.get_width() / 2 - self.title[0].get_width() / 2
            )
        self.title_pos: tuple[int, int] = (title_width, 100)

        # Background
        path: str = './src/pacman/app/images/bg-frames'
        dir_list: list[str] = sorted(
            os.listdir(path),
            key=lambda x: int(x[x.find('_') + 1:x.find('.')])
            )
        self.bg: list[pg.Surface] = [pg.image.load(f'{path}/{frame}').convert()
                                     for frame in dir_list]
        bg_x: int = int(
            self.screen.get_width() / 2 - self.bg[0].get_width() / 2
            )
        bg_y: int = int(
            self.screen.get_height() / 2 - self.bg[0].get_height() / 2
            )
        self.bg_pos: tuple[int, int] = (bg_x, bg_y)

        # Character Selection screen settings
        self.queen_1: Button = Button('queen-1.png',
                                      'queen-1-hover.png')
        x: int = int(
            self.screen.get_width() / 4 - self.queen_1.button.get_width() / 2
            )
        y: int = 200
        self.queen_1.pos = (x, y)
        self.queen_2: Button = Button('queen-2.png',
                                      'queen-2-hover.png',
                                      hover_offset=(10, 30))
        x = int(
            self.screen.get_width() / 4 * 3
            - self.queen_2.button.get_width() / 2
            )
        y = (self.queen_1.button.get_height() -
             self.queen_2.button.get_height() + 201)
        self.queen_2.pos = (x, y)
        self.QUEENS: Final = [self.queen_1, self.queen_2]

        # Choose your diva and Queen Names
        self.choose: pg.Surface = (
            pg.image
              .load(f'{self.exit.IMAGES}/select-your-diva.png')
              .convert_alpha()
              )
        self.waka: pg.Surface = (
            pg.image
              .load(f'{self.exit.IMAGES}/waka-waka-wanda.png')
              .convert_alpha()
              ) 
        self.ms_pellet: pg.Surface = (
            pg.image
              .load(f'{self.exit.IMAGES}/ms-power-pellet.png')
              .convert_alpha()
              )
        choose_width: int = int(
            self.screen.get_width() / 2 - self.choose.get_width() / 2
            )
        self.choose_pos: tuple[int, int] = (choose_width, 100)
        waka_width: int = self.queen_1.pos[0] + self.queen_1.width + 10
        self.waka_pos: tuple[int, int] = (waka_width,
                                          self.queen_1.pos[1] + 250)
        ms_pellet_width: int = (self.queen_2.pos[0]
                                - self.ms_pellet.get_width()) - 10
        ms_pellet_height: int = self.queen_2.height + self.queen_2.pos[1] - 75
        self.ms_pellet_pos: tuple[int, int] = (ms_pellet_width,
                                               ms_pellet_height)

    def render_main_menu(self) -> None:
        """Render main menu"""
        start_time: float = time.time() * 1000
        while self.running:
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

            if not self.start_game.clicked:
                title_frame: int = (
                    (int(now - start_time) // 125)
                    % len(self.title)
                    )
                self.screen.blit(self.title[title_frame],
                                 self.title_pos)

                # render buttons
                for button in self.BUTTONS:
                    if button.hovering(mx, my):
                        button.render_hover_button(self.screen)
                    else:
                        button.render_button(self.screen)

                for event in pg.event.get():
                    for button in self.BUTTONS:
                        if (event.type == pg.MOUSEBUTTONDOWN
                           and button.hovering(mx, my)):
                            button.clicked = True
                            if button == self.exit:
                                self.running = False
            else:
                for queen in self.QUEENS:
                    if queen.hovering(mx, my):
                        queen.render_hover_button(self.screen)
                    else:
                        queen.render_button(self.screen)
                    self.screen.blit(self.choose, self.choose_pos)
                    self.screen.blit(self.waka, self.waka_pos)
                    self.screen.blit(self.ms_pellet, self.ms_pellet_pos)

                for event in pg.event.get():
                    for queen in self.QUEENS:
                        if (event.type == pg.MOUSEBUTTONDOWN
                           and queen.hovering(mx, my)):
                            queen.clicked = True

            pg.display.flip()

    def _test_actions(self) -> None:
        """Test actions until there is proper actions in-place."""
        print("Game started." if self.start_game.clicked
              else "Game not started.")
        print("High Scores clicked." if self.start_game.clicked
              else "High Scores not clicked.")
        print("Instructions were shown." if self.instr.clicked
              else "Instructions were not shown.")
        print("Waka Waka Wanda was chosen." if self.queen_1.clicked
              else "Waka Waka Wanda wasn't chosen.")
        print("Ms. Power Pellet was chosen." if self.queen_2.clicked
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


def start_UI() -> None:
    """Main function for starting the UI."""

    with UI() as ui:
        ui.render_main_menu()
        ui._test_actions()


if __name__ == "__main__":
    start_UI()
