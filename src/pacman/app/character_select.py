"""Render character selection and report the selected character."""

from typing import Final

import pygame as pg

from pacman.app.menu_actions import CharSelectAction
from pacman.app.ui_assets import IMAGES, center, load_trans_image
from pacman.app.ui_button import Button


class CharacterSelect:
    """Character Select screen."""

    def __init__(self, screen: pg.Surface) -> None:
        """Create a character select screen.

        Args:
            screen (pg.Surface): screen to display the graphics."""
        self.queen_1: Button = Button(
            'queen-1.png',
            'queen-1-hover.png',
            hover_offset=(60, 30)
        )
        x: int = center(
            screen.get_width() // 2,
            self.queen_1.button.get_width()
        )
        y: int = 200
        self.queen_1.pos = (x, y)

        self.queen_2: Button = Button(
            'queen-2.png',
            'queen-2-hover.png',
            hover_offset=(10, 30)
        )
        x = int(
            screen.get_width() / 4 * 3
            - self.queen_2.button.get_width() / 2
        )
        y = (
            self.queen_1.button.get_height()
            - self.queen_2.button.get_height()
            + y
            + 1
        )
        self.queen_2.pos = (x, y)
        self.QUEENS: Final = [self.queen_1, self.queen_2]

        # Choose your diva and Queen Names
        self.choose: pg.Surface = load_trans_image(
            f'{IMAGES}/select-your-diva.png'
        )
        self.waka: pg.Surface = load_trans_image(
            f'{IMAGES}/waka-waka-wanda.png'
        )
        self.ms_pellet: pg.Surface = load_trans_image(
            f'{IMAGES}/ms-power-pellet.png'
        )

        choose_x: int = center(
            screen.get_width(),
            self.choose.get_width()
        )
        self.choose_pos: tuple[int, int] = (choose_x, 100)

        waka_x: int = (
            self.queen_1.pos[0]
            + self.queen_1.width
            + 10
        )
        self.waka_pos: tuple[int, int] = (
            waka_x,
            self.queen_1.pos[1] + 100
        )

        ms_pellet_x: int = (
            self.queen_2.pos[0]
            - self.ms_pellet.get_width()
        ) - 10
        ms_pellet_y: int = (
            self.queen_2.height
            + self.queen_2.pos[1]
            - 75
        )
        self.ms_pellet_pos: tuple[int, int] = (
            ms_pellet_x,
            ms_pellet_y
        )

        self.back_button: Button = Button(
            'go-back-symbol.png',
            'go-back-symbol-hover.png',
            pos=(0, screen.get_height() - 140),
            hover_offset=(-20, 50)
        )
        self.back_to_main: pg.Surface = load_trans_image(
            f'{IMAGES}/back-to-main-menu.png'
        )
        self.back_to_main_pos: tuple[int, int] = (
            10,
            screen.get_height() - 40
        )

    def render_char_select(
        self,
        mouse: tuple[int, int],
        screen: pg.Surface
    ) -> None:
        """Render the character select. Runs in the main loop.

        Args:
            mouse (tuple[int, int]): mouse positions in x,y
            screen (pg.Surface): screen displaying the graphics"""

        mx, my = mouse

        for queen in self.QUEENS:
            if queen.hovering(mx, my):
                queen.render_hover_button(screen)
            else:
                queen.render_button(screen)

        if self.back_button.hovering(mx, my):
            self.back_button.render_hover_button(screen)
        else:
            self.back_button.render_button(screen)

        screen.blit(self.choose, self.choose_pos)
        screen.blit(self.waka, self.waka_pos)
        screen.blit(self.ms_pellet, self.ms_pellet_pos)
        screen.blit(self.back_to_main, self.back_to_main_pos)

    def handle_event(
        self,
        event: pg.event.Event,
    ) -> CharSelectAction | None:
        """Handle events from character select screen.

        Args:
            event (pg.event.Event): Pygame Event, here pressing mouse

        Returns:
            CharSelectAction | None: Action from character select screen."""
        if event.type == pg.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if self.queen_1.hovering(mx, my):
                return CharSelectAction.WAKA_WAKA_WANDA
            elif self.queen_2.hovering(mx, my):
                return CharSelectAction.MS_POWER_PELLET
            elif self.back_button.hovering(mx, my):
                return CharSelectAction.MAIN_MENU

        return None
