import pygame as pg
from pacman.app.actions import (center,
                                load_trans_image,
                                IMAGES)


class PauseMenu():
    def __init__(self,
                 screen: pg.Surface) -> None:
        self.font: pg.font.Font = pg.font.Font(
         "src/pacman/app/assets/PressStart2P-Regular.ttf", 20)
        self.main_menu: pg.Surface = self.font.render(
            'Back to Main Menu',
            True,
            color='white'
            )
        self.change_char: pg.Surface = self.font.render(
            'Change Queen',
            True,
            color='white'
            )
        self.quit_game: pg.Surface = self.font.render(
            'Quit Game',
            True,
            color='white'
        )
        self.restart_level: pg.Surface = self.font.render(
            'Restart Level',
            True,
            color='white'
        )
        self.quit_menu: pg.Surface = self.font.render(
            'X',
            True,
            color='red'
        )
        self.screen: pg.Surface = screen
        self.frame: pg.Surface = load_trans_image(f'{IMAGES}/pause-frame.png')

    def render_pause_menu(self) -> None:
        self.screen.fill(color='darkgrey', special_flags=pg.BLEND_MULT)

        x: int = center(self.screen.get_width(),
                        self.frame.get_width())
        y: int = center(self.screen.get_height(),
                        self.frame.get_height())
        self.screen.blit(self.frame, (x, y))

        x = center(self.screen.get_width(),
                   self.main_menu.get_width())
        self.screen.blit(self.main_menu, (x, 400))

        x = center(self.screen.get_width(),
                   self.restart_level.get_width())
        self.screen.blit(self.restart_level, (x, 450))

        x = center(self.screen.get_width(),
                   self.change_char.get_width())
        self.screen.blit(self.change_char, (x, 500))

        x = center(self.screen.get_width(),
                   self.quit_game.get_width())
        self.screen.blit(self.quit_game, (x, 550))

        x = center(self.screen.get_width(),
                   self.quit_game.get_width())
        self.screen.blit(self.quit_menu, (x + self.frame.get_width() // 2 - 10, 350))
