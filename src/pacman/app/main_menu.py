"""Render and handle actions from the animated main menu."""

import time
from typing import Final

import pygame as pg

from pacman.app.menu_actions import MainMenuAction
from pacman.app.ui_assets import IMAGES, center, load_trans_image
from pacman.app.ui_button import Button


class MainMenu:
    def __init__(self, screen: pg.Surface) -> None:
        R_DIST_FROM_CNTR: Final = 25
        L_DIST_FROM_CNTR: Final = 430
        button_r: int = screen.get_width() // 2 + R_DIST_FROM_CNTR
        button_l: int = screen.get_width() // 2 - L_DIST_FROM_CNTR
        height: int = 400
        BTTN_W: Final = 450

        # Start Game settings
        self.start_game: Button = Button(
            'start-game.png',
            'start-game-hover.png',
            pos=(button_l - BTTN_W, height),
        )

        # High Scores settings
        self.high_scores: Button = Button(
            'high-scores.png',
            'high-scores-hover.png',
            pos=(button_l, height),
        )

        # Instructions settings
        self.instr: Button = Button(
            'instructions.png',
            'instructions-hover.png',
            pos=(button_r, height),
        )

        # Exit settings
        self.exit: Button = Button(
            'sashay-away.png',
            'sashay-away-hover.png',
            pos=(button_r + BTTN_W, height),
        )

        self.BUTTONS: Final = [
            self.start_game,
            self.high_scores,
            self.instr,
            self.exit,
        ]

        # Title settings
        self.title: list[pg.Surface] = [
            load_trans_image(f'{IMAGES}/title_{i}.png')
            for i in range(1, 6)
        ]
        title_width: int = center(
            screen.get_width(),
            self.title[0].get_width(),
        )
        self.title_pos: tuple[int, int] = (title_width, 100)

    def render_main_menu(
        self,
        start_time: float,
        mouse: tuple[int, int],
        screen: pg.Surface
    ) -> None:
        now: float = time.time() * 1000
        mx, my = mouse
        title_frame: int = (
            (int(now - start_time) // 125)
            % len(self.title)
        )
        screen.blit(
            self.title[title_frame],
            self.title_pos,
        )

        # render buttons
        for button in self.BUTTONS:
            if button.hovering(mx, my):
                button.render_hover_button(screen)
            else:
                button.render_button(screen)

    def handle_event(
        self,
        event: pg.event.Event,
    ) -> MainMenuAction | None:
        if event.type == pg.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if self.start_game.hovering(mx, my):
                return MainMenuAction.START_GAME
            elif self.instr.hovering(mx, my):
                return MainMenuAction.SHOW_INSTRUCTIONS
            elif self.high_scores.hovering(mx, my):
                return MainMenuAction.VIEW_HIGHSCORES
            elif self.exit.hovering(mx, my):
                return MainMenuAction.EXIT

        return None
