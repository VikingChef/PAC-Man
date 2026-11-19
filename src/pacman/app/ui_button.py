"""Reusable image button for application menus."""

import pygame as pg

from pacman.app.ui_assets import IMAGES, load_trans_image


class Button:
    """Button class generates button objects, like Start Game."""

    def __init__(
        self,
        path: str,
        hover_path: str,
        pos: tuple[int, int] = (0, 0),
        hover_offset: tuple[int, int] = (45, 30)
    ) -> None:
        """Initialize a Button object.

        Args:
            path (str): file path to the image.
            hover_path (str): file path to the alternative for hoverring.
            pos (tuple[int, int]): position of the image in x, y.
        """
        self.button: pg.Surface = load_trans_image(f'{IMAGES}/{path}')
        self.hover_button: pg.Surface = load_trans_image(
            f'{IMAGES}/{hover_path}'
        )
        self.pos: tuple[int, int] = pos
        self.x, self.y = self.pos
        self.width, self.height = (
            self.button.get_width(),
            self.button.get_height(),
        )
        self.hover_offset: tuple[int, int] = hover_offset

    @property
    def hover_pos(self) -> tuple[int, int]:
        return (
            self.pos[0] - self.hover_offset[0],
            self.pos[1] - self.hover_offset[1],
        )

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
        return (
            self.pos[0] <= mx <= self.width + self.pos[0]
            and self.pos[1] <= my <= self.height + self.pos[1]
        )
