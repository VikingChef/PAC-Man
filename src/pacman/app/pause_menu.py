import pygame as pg
from pacman.app.actions import (center,
                                load_trans_image,
                                IMAGES)
from enum import Enum, auto


class PauseMenuAction(Enum):
    BACK_TO_MAIN_MENU = auto()
    CHANGE_QUEEN = auto()
    QUIT_GAME = auto()
    RESTART_LEVEL = auto()


class Button:
    """Button class generates button objects."""

    def __init__(
        self,
        text: str,
        font: pg.font.Font,
        color: str,
        screen: pg.Surface,
        pos: tuple[int, int] = (0, 0)
    ) -> None:
        """Initialize a Button object.

        Args:
            path (str): file path to the image.
            hover_path (str): file path to the alternative for hoverring.
            pos (tuple[int, int]): position of the image in x, y.
        """
        self.button: pg.Surface = font.render(
            text,
            True,
            color=color
        )
        self.pos: tuple[int, int] = pos
        self.x, self.y = self.pos
        self.width, self.height = (
            self.button.get_width(),
            self.button.get_height(),
        )
        self.screen = screen

    def render(self) -> None:
        """Render a button in a pre-made screen.

        Args:
            screen (pg.Surface): screen created by pygame.
        """
        self.screen.blit(self.button, self.pos)

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


class PauseMenu():

    def __init__(self,
                 screen: pg.Surface) -> None:
        self.font: pg.font.Font = pg.font.Font(
         "src/pacman/app/assets/PressStart2P-Regular.ttf", 20)
        self.main_menu: Button = Button(
            'Back to Main Menu',
            self.font,
            color='white',
            screen=screen
        )

        self.change_char: Button = Button(
            'Change Queen',
            self.font,
            color='white',
            screen=screen
        )
        self.quit_game: Button = Button(
            'Quit Game',
            self.font,
            color='white',
            screen=screen
        )
        self.restart_level: Button = Button(
            'Restart Level',
            self.font,
            color='white',
            screen=screen
        )
        self.quit_menu: Button = Button(
            'X',
            self.font,
            color='white',
            screen=screen
        )
        self.screen: pg.Surface = screen
        self.frame: pg.Surface = load_trans_image(f'{IMAGES}/pause-frame.png')
        self.hover: pg.Surface = load_trans_image(f'{IMAGES}/choose-frame.png')

    def render_pause_menu(self) -> None:
        mx, my = pg.mouse.get_pos()
        self.screen.fill(color='darkgrey', special_flags=pg.BLEND_MULT)

        x: int = center(self.screen.get_width(),
                        self.frame.get_width())
        y: int = center(self.screen.get_height(),
                        self.frame.get_height())
        self.screen.blit(self.frame, (x, y))

        x = center(self.screen.get_width(),
                   self.main_menu.button.get_width())
        y = (center(self.screen.get_height(),
                    self.main_menu.button.get_height()) -
             self.restart_level.button.get_height() - 100)
        self.main_menu.pos = x, y
        choose_x: int = x - 10
        self.main_menu.render()
        if self.main_menu.hovering(mx, my):
            self.screen.blit(self.hover, (choose_x, y - 10))

        x = center(self.screen.get_width(),
                   self.restart_level.button.get_width())
        y = center(self.screen.get_height(),
                   self.restart_level.button.get_height()) - 25
        self.restart_level.pos = x, y
        self.restart_level.render()
        if self.restart_level.hovering(mx, my):
            self.screen.blit(self.hover, (choose_x, y - 10))

        x = center(self.screen.get_width(),
                   self.change_char.button.get_width())
        y = center(self.screen.get_height(),
                   self.change_char.button.get_height()) + 50
        self.change_char.pos = x, y
        self.change_char.render()
        if self.change_char.hovering(mx, my):
            self.screen.blit(self.hover, (choose_x, y - 10))

        x = center(self.screen.get_width(),
                   self.quit_game.button.get_width())
        y = (center(self.screen.get_height(),
                    self.quit_game.button.get_height()) +
             self.change_char.button.get_height() + 100)
        self.quit_game.pos = x, y
        self.quit_game.render()
        if self.quit_game.hovering(mx, my):
            self.screen.blit(self.hover, (choose_x, y - 10))

    def handle_event(self,
                     event: pg.event.Event) -> PauseMenuAction:
        mx, my = event.pos

        if self.main_menu.hovering(mx, my):
            return PauseMenuAction.BACK_TO_MAIN_MENU
        elif self.quit_game.hovering(mx, my):
            return PauseMenuAction.QUIT_GAME
        elif self.change_char.hovering(mx, my):
            return PauseMenuAction.CHANGE_QUEEN
        elif self.restart_level.hovering(mx, my):
            return PauseMenuAction.RESTART_LEVEL

        return None
