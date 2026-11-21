import pygame as pg
import time

from pacman.app.highscore_select import FONT_PATH
from pacman.app.actions import Button, center, load_trans_image, IMAGES


class VictoryScreen:
    def __init__(self, screen: pg.Surface, score: int) -> None:
        """Prepare the funeral artwork, fonts and button positions."""
        self.screen = screen
        self.artwork = Button(
            'victory.png',
            'victory-hover.png',
            hover_offset=(0, 0)
        )
        self.artwork.pos = (
            center(screen.get_width(), self.artwork.width),
            center(screen.get_height(), self.artwork.height)
        )

        self.title_font = pg.font.Font(FONT_PATH, 50)

        self.white = (235, 230, 230)

        self.background: pg.Surface | None = None

        self.original_background: pg.Surface | None = None
        self.score = score
        self.hover = pg.Rect(644, 696, 626, 96)
        self.firework = [load_trans_image(f'{IMAGES}/fireworks/frame_{i}.gif')
                         for i in range(1, 30)]
        self.start_time = time.time() * 1000

    @property
    def score_text(self) -> pg.Surface:
        return self.title_font.render(
            str(self.score),
            True,
            color=self.white
            )

    def render_victory(self) -> None:
        mx, my = pg.mouse.get_pos()
        now = time.time() * 1000
        frwrk_frm = (
            (int(now - self.start_time) // 65)
            % len(self.firework)
        )

        if (mx >= self.hover.left and mx <= self.hover.right
           and my >= self.hover.top and my <= self.hover.bottom):
            self.artwork.render_button(self.screen)
        else:
            self.artwork.render_hover_button(self.screen)
        score_pos = (
            center(self.screen.get_width(),
                   self.score_text.get_width()),
            center(self.screen.get_height(),
                   self.score_text.get_height()) + 50,
        )
        if int(time.time()) % 2 == 0:
            self.screen.blit(self.score_text, score_pos)
        self.screen.blit(self.firework[frwrk_frm], (500, 500)) 
        self.screen.blit(self.firework[frwrk_frm], (1150, 300))
        self.screen.blit(self.firework[frwrk_frm], (1050, 475))
