#!/usr/bin/env python3
"""Shared application actions for Pac-Man."""

from enum import Enum, auto
from typing import Final
from types import TracebackType
import pygame as pg


class MainMenuAction(Enum):
    """Actions available from the Pac-Man main menu."""

    # Define the choices the UI can return to the orchestrator.
    START_GAME = auto()
    VIEW_HIGHSCORES = auto()
    SHOW_INSTRUCTIONS = auto()
    EXIT = auto()


class UI:
    """Main Page for UI"""
    HOT_PINK: Final = (248, 74, 204)
    IMAGES: Final = 'src/pacman/app/images'
    START_GAME_POS: Final = (50, 50)
    START_GAME_HOVER_POS: Final = (15, 20)

    def __init__(self):
        self.screen: pg.Surface = pg.display.set_mode(flags=pg.FULLSCREEN)
        self.running: bool = True
        self.start_game: pg.Surface = (
            pg.image
              .load(f'{self.IMAGES}/start-game.png')
              .convert_alpha()
              )
        self.start_game_hover: pg.Surface = (
            pg.image
            .load(f'{self.IMAGES}/start-game-hover.png')
            .convert_alpha()
            )
        self.start_x: int = self.START_GAME_POS[0]
        self.start_y: int = self.START_GAME_POS[1]
        self.start_width: int = self.start_game.get_width()
        self.start_height: int = self.start_game.get_height()
        self.start_game_clicked: bool = False

    def render_main_menu(self) -> None:
        """Render main menu"""
        while self.running:
            mx, my = pg.mouse.get_pos()
            hovering_on_start_game: bool = (
                self.start_x <= mx <= self.start_width + self.start_x
                and self.start_y <= my <= self.start_height + self.start_y)

            # tracking events such as quitting the program
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False

                if event.type == pg.MOUSEBUTTONDOWN and hovering_on_start_game:
                    self.start_game_clicked = True

            self.screen.fill(self.HOT_PINK)

            # render buttons
            if hovering_on_start_game:
                self.screen.blit(self.start_game_hover,
                                 self.START_GAME_HOVER_POS)
            else:
                self.screen.blit(self.start_game, self.START_GAME_POS)
            pg.display.flip()

    def _test_actions(self) -> None:
        """Test actions until there is proper actions in-place."""
        print("Game started." if self.start_game_clicked
              else "Game not started.")

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
