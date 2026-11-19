"""Render incremental background-loading progress."""

import pygame as pg

from pacman.app.ui_assets import IMAGES, center, load_trans_image


class LoadingBar:
    def __init__(self, screen: pg.Surface) -> None:
        path: str = f'{IMAGES}/loading-frames'
        self.frames: list[pg.Surface] = [
            load_trans_image(f'{path}/frame_{i}.png')
            for i in range(5)
        ]
        x: int = center(
            screen.get_width(),
            self.frames[0].get_width(),
        )
        y: int = center(
            screen.get_height(),
            self.frames[0].get_height(),
        )
        self.frame_pos: tuple[int, int] = (x, y)

        self.text: pg.Surface = load_trans_image(
            f'{IMAGES}/loading.png'
        )
        x = center(
            screen.get_width(),
            self.text.get_width(),
        )
        y += self.frames[0].get_height() + 10
        self.text_pos: tuple[int, int] = (x, y)
        self.screen: pg.Surface = screen

    def render_bar(self, frame: int) -> None:
        self.screen.fill((255, 255, 255))
        self.screen.blit(
            self.frames[frame],
            self.frame_pos
        )
        self.screen.blit(
            self.text,
            self.text_pos
        )
