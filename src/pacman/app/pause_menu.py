"""Draw Ilias's pause menu and report the player's chosen action."""

from enum import Enum, auto
from pathlib import Path

import pygame as pg

from pacman.app.ui_assets import IMAGES, center, load_trans_image


FONT_PATH = "src/pacman/app/assets/PressStart2P-Regular.ttf"


class PauseMenuAction(Enum):
    """Choices offered by the paused game interface."""

    BACK_TO_MAIN_MENU = auto()
    CHANGE_QUEEN = auto()
    QUIT_GAME = auto()
    RESTART_LEVEL = auto()
    RESUME_GAME = auto()


class PauseButton:
    """Display one pause-menu label and detect clicks on its bounds."""

    def __init__(
        self,
        text: str,
        font: pg.font.Font,
    ) -> None:
        """Build text once and keep its clickable rectangle available."""
        self.image = font.render(text, True, "white")
        self.rect = self.image.get_rect()

    def place(self, position: tuple[int, int]) -> None:
        """Position both the rendered label and its hitbox."""
        self.rect.topleft = position

    def hovering(self, position: tuple[int, int]) -> bool:
        """Check whether a logical canvas position overlaps the label."""
        return self.rect.collidepoint(position)


class PauseMenu:
    """Own pause-menu presentation without changing gameplay state."""

    def __init__(self, screen: pg.Surface) -> None:
        """Load the menu artwork and prepare its interactive labels."""
        self.screen = screen
        self.font = pg.font.Font(FONT_PATH, 20)
        self.italics_font = pg.font.Font(FONT_PATH, 10)
        self.italics_font.italic = True
        self.main_menu = PauseButton("Back to Main Menu", self.font)
        self.restart_level = PauseButton("Restart Level", self.font)
        self.change_char = PauseButton("Change Queen", self.font)
        self.quit_game = PauseButton("Quit Game", self.font)

        # Keep the artwork from Ilias's UI branch when it is present.
        # A drawn frame also lets the menu run before those assets merge.
        frame_path = Path(IMAGES) / "pause-frame.png"
        hover_path = Path(IMAGES) / "choose-frame.png"
        self.frame = (
            load_trans_image(str(frame_path))
            if frame_path.is_file() else None
        )
        self.hover = (
            load_trans_image(str(hover_path))
            if hover_path.is_file() else None
        )

        self.buttons = (
            (self.main_menu, PauseMenuAction.BACK_TO_MAIN_MENU),
            (self.restart_level, PauseMenuAction.RESTART_LEVEL),
            (self.change_char, PauseMenuAction.CHANGE_QUEEN),
            (self.quit_game, PauseMenuAction.QUIT_GAME),
        )
        self.hint = self.italics_font.render(
            'Press [SPACE] to unpause.',
            True,
            color='white'
            )

        self._place_buttons()

    def _place_buttons(self) -> None:
        """Lay out every hitbox before input or drawing occurs."""
        screen_width, screen_height = self.screen.get_size()
        vertical_center = screen_height // 2
        entries = (
            (self.main_menu, -125),
            (self.restart_level, -45),
            (self.change_char, 35),
            (self.quit_game, 115),
        )

        for button, offset in entries:
            button.place((
                center(screen_width, button.rect.width),
                vertical_center + offset,
            ))

    def render_pause_menu(
        self,
        mouse_position: tuple[int, int],
    ) -> None:
        """Draw the paused overlay with canvas-relative hover feedback."""
        # The caller draws the frozen game first; darken it here.
        shade = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        shade.fill((12, 8, 24, 190))
        self.screen.blit(shade, (0, 0))

        if self.frame is not None:
            frame_position = (
                center(self.screen.get_width(), self.frame.get_width()),
                center(self.screen.get_height(), self.frame.get_height()),
            )
            self.screen.blit(self.frame, frame_position)

            hint_position = (
                center(self.screen.get_width(), self.hint.get_width()),
                frame_position[1] + 80
            )
            self.screen.blit(self.hint, hint_position)
        else:
            frame_rect = pg.Rect(0, 0, 650, 470)
            frame_rect.center = self.screen.get_rect().center
            pg.draw.rect(self.screen, (42, 23, 67), frame_rect,
                         border_radius=24)
            pg.draw.rect(self.screen, (204, 105, 210), frame_rect,
                         width=4, border_radius=24)

        for button, _ in self.buttons:
            if button.hovering(mouse_position):
                if self.hover is not None:
                    hover_position = (
                        button.rect.centerx - self.hover.get_width() // 2,
                        button.rect.centery - self.hover.get_height() // 2,
                    )
                    self.screen.blit(self.hover, hover_position)
                else:
                    outline = button.rect.inflate(32, 24)
                    pg.draw.rect(self.screen, (171, 88, 199), outline,
                                 width=2, border_radius=8)
            self.screen.blit(button.image, button.rect)

    def handle_event(
        self,
        event: pg.event.Event,
    ) -> PauseMenuAction | None:
        """Return a choice only for a left-click inside a button."""
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return None

        for button, action in self.buttons:
            if button.hovering(event.pos):
                return action
        return None
