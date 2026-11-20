
"""Display and handle leaderboard name entry."""

from __future__ import annotations

from enum import Enum, auto
from pathlib import Path

import pygame as pg

from pacman.app.pause_menu import FONT_PATH, PauseButton
from pacman.app.ui_assets import IMAGES, center, load_trans_image
from pacman.game.run_finalizer import EntryKind


class NameEntryAction(Enum):
    """Choices available during leaderboard name entry."""

    SUBMIT = auto()
    EXIT = auto()
    MAIN_MENU = auto()


class NameEntryScreen:
    """Collect a player's Hall of Fame or Center of Shade name."""

    def __init__(self, screen: pg.Surface) -> None:
        """Prepare the existing arcade artwork and input controls."""
        self.screen = screen
        self.kind: EntryKind | None = None
        self.name = ""
        self.max_length = 3

        # Reuse the same pixel font as Ilias's pause menu.
        self.title_font = pg.font.Font(FONT_PATH, 20)
        self.text_font = pg.font.Font(FONT_PATH, 12)
        self.input_font = pg.font.Font(FONT_PATH, 20)
        self.small_font = pg.font.Font(FONT_PATH, 10)
        self.button_font = pg.font.Font(FONT_PATH, 16)

        self.white = (255, 255, 255)
        self.gold = (255, 220, 90)
        self.pink = (255, 140, 220)

        # Use the original graphics without stretching their pixels.
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

        # Reuse the pause menu's existing button implementation.
        self.submit_button = PauseButton(
            "Submit",
            self.button_font,
        )
        self.back_button = PauseButton(
            "Back to Main Menu",
            self.button_font,
        )

        self.buttons = (
            (self.submit_button, NameEntryAction.SUBMIT),
            (self.back_button, NameEntryAction.MAIN_MENU),
        )

        self._place_buttons()

    def _place_buttons(self) -> None:
        """Position buttons relative to the menu's center."""
        width, height = self.screen.get_size()
        middle = height // 2

        self.submit_button.place((
            center(width, self.submit_button.rect.width),
            middle + 65,
        ))
        self.back_button.place((
            center(width, self.back_button.rect.width),
            middle + 125,
        ))

    def begin(self, kind: EntryKind) -> None:
        """Prepare a new name field for the selected leaderboard."""
        self.kind = kind
        self.name = ""
        self.max_length = 3 if kind == EntryKind.FAME else 10

    def handle_event(
        self,
        event: pg.event.Event,
    ) -> NameEntryAction | None:
        """Process keyboard input and existing menu-button clicks."""
        if self.kind is None:
            return None

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return NameEntryAction.EXIT

            if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                return NameEntryAction.SUBMIT

            if event.key == pg.K_BACKSPACE:
                self.name = self.name[:-1]
                return None

            character = event.unicode.upper()

            if not character.isascii() or not character.isprintable():
                return None

            # Hall of Fame initials must be three ASCII letters.
            if self.kind == EntryKind.FAME:
                if not character.isalpha():
                    return None

            if len(self.name) + len(character) <= self.max_length:
                self.name += character

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button != 1:
                return None

            for button, action in self.buttons:
                if button.hovering(event.pos):
                    return action

        return None

    def _draw_text(
        self,
        message: str,
        font: pg.font.Font,
        color: tuple[int, int, int],
        center_y: int,
    ) -> None:
        """Draw centered text using the established pixel font."""
        image = font.render(message, True, color)
        position = (
            center(self.screen.get_width(), image.get_width()),
            center_y - image.get_height() // 2,
        )
        self.screen.blit(image, position)

    def _draw_frame(self) -> None:
        """Display Ilias's original pause-frame artwork."""
        if self.frame is not None:
            position = (
                center(
                    self.screen.get_width(),
                    self.frame.get_width(),
                ),
                center(
                    self.screen.get_height(),
                    self.frame.get_height(),
                ),
            )
            self.screen.blit(self.frame, position)

        else:
            # Keep the interface usable if assets are unavailable.
            rectangle = pg.Rect(0, 0, 650, 470)
            rectangle.center = self.screen.get_rect().center
            pg.draw.rect(
                self.screen,
                (42, 23, 67),
                rectangle,
                border_radius=24,
            )
            pg.draw.rect(
                self.screen,
                (204, 105, 210),
                rectangle,
                width=4,
                border_radius=24,
            )

    def _draw_buttons(
        self,
        mouse_position: tuple[int, int],
    ) -> None:
        """Render buttons with Ilias's existing hover artwork."""
        for button, _ in self.buttons:
            if button.hovering(mouse_position):
                if self.hover is not None:
                    position = (
                        button.rect.centerx
                        - self.hover.get_width() // 2,
                        button.rect.centery
                        - self.hover.get_height() // 2,
                    )
                    self.screen.blit(self.hover, position)
                else:
                    outline = button.rect.inflate(32, 24)
                    pg.draw.rect(
                        self.screen,
                        (171, 88, 199),
                        outline,
                        width=2,
                        border_radius=8,
                    )

            self.screen.blit(button.image, button.rect)

    def render(self, mouse_position: tuple[int, int]) -> None:
        """Render the name-entry screen with existing arcade assets."""
        if self.kind is None:
            return

        self.screen.fill((12, 8, 24))
        self._draw_frame()

        middle = self.screen.get_height() // 2

        if self.kind == EntryKind.FAME:
            title = "HALL OF FAME"
            message = "YOUR SCORE HAS EARNED ITS CROWN"
            prompt = "ENTER THREE INITIALS"
        else:
            title = "CENTER OF SHADE"
            message = "WE KNOW WHAT YOU DID"
            prompt = "ENTER YOUR NAME"

        self._draw_text(
            title,
            self.title_font,
            self.gold,
            middle - 150,
        )
        self._draw_text(
            message,
            self.small_font,
            self.white,
            middle - 100,
        )
        self._draw_text(
            prompt,
            self.text_font,
            self.pink,
            middle - 58,
        )

        display_name = self.name + "_" * (
            self.max_length - len(self.name)
        )

        self._draw_text(
            display_name,
            self.input_font,
            self.gold,
            middle,
        )

        self._draw_buttons(mouse_position)

        self._draw_text(
            "(NO NAME? WE'LL CALL YOU ASS.)",
            self.small_font,
            self.white,
            middle + 165,
        )
