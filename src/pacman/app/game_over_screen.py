"""Display the royal Game Over tribunal and its mercy choices."""

import time
from enum import Enum, auto
from pathlib import Path

import pygame as pg

from pacman.app.game_over_background import create_greyscale_background
from pacman.app.pause_menu import FONT_PATH
from pacman.app.pixel_fading import blend_pixels
from pacman.app.ui_assets import IMAGES


class GameOverAction(Enum):
    """Identify the player's response to the royal tribunal."""

    BEG_FOR_MERCY = auto()
    SASHAY_AWAY = auto()


class GameOverScreen:
    """Present defeat, mercy choices and the royal refusal."""

    def __init__(self, screen: pg.Surface) -> None:
        """Prepare the funeral artwork, fonts and button positions."""
        self.screen = screen
        self.artwork = pg.image.load(
            str(Path(IMAGES) / "game_over.png")
        ).convert_alpha()

        self.title_font = pg.font.Font(FONT_PATH, 17)
        self.text_font = pg.font.Font(FONT_PATH, 14)
        self.button_font = pg.font.Font(FONT_PATH, 12)

        self.white = (235, 230, 230)
        self.silver = (190, 190, 195)
        self.red = (210, 70, 80)

        self.refused = False
        self.background: pg.Surface | None = None
        self.original_background: pg.Surface | None = None
        self.fade_started_at: float | None = None

        screen_center = self.screen.get_rect().center
        self.panel = self.artwork.get_rect(
            center=(screen_center[0], screen_center[1] + 35)
        )

        # The button art occupies y=365..440 within the 650x470 panel.
        # These rectangles serve both text placement and mouse handling.
        self.mercy_button = pg.Rect(
            self.panel.left + 65,
            self.panel.top + 365,
            240,
            75,
        )
        self.leave_button = pg.Rect(
            self.panel.left + 325,
            self.panel.top + 365,
            240,
            75,
        )

    def begin(self) -> None:
        """Prepare a fresh royal tribunal."""
        self.refused = False
        self.background = None
        self.original_background = None
        self.fade_started_at = None

    def show_refusal(self) -> None:
        """Display the royal response to a second plea."""
        self.refused = True

    def _draw_text(
        self,
        message: str,
        font: pg.font.Font,
        color: tuple[int, int, int],
        center_y: int,
    ) -> None:
        """Draw one centered line of arcade text."""
        image = font.render(message, True, color)
        position = image.get_rect(
            center=(self.panel.centerx, center_y)
        )
        self.screen.blit(image, position)

    def render(self) -> None:
        """Render the frozen game and royal funeral tribunal."""
        if self.background is None:
            # Capture the last gameplay frame once per Game Over.
            self.original_background = self.screen.copy().convert()
            self.background = create_greyscale_background(
                self.original_background
            )
            self.fade_started_at = time.monotonic()

        if (
            self.original_background is not None
            and self.fade_started_at is not None
            and self.background is not None
        ):
            elapsed = time.monotonic() - self.fade_started_at
            progress = min(elapsed / 1.2, 1.0)

            if progress >= 1.0:
                faded_background = self.background
            else:
                faded_background = blend_pixels(
                    self.original_background,
                    self.background,
                    progress,
                )

            # Keep the working fade: write RGB values to the canvas.
            colours = pg.surfarray.array3d(faded_background)
            canvas_pixels = pg.surfarray.pixels3d(self.screen)
            canvas_pixels[:, :, :] = colours
            del canvas_pixels

        # The funeral artwork stays coloured above the grey maze.
        self.screen.blit(self.artwork, self.panel.topleft)

        # Title sits inside the red banner, clear of its silver rim.
        self._draw_text(
            "GAME OVER, DARLING.",
            self.title_font,
            self.white,
            self.panel.top + 93,
        )

        self._draw_text(
            "A QUEEN HAS FALLEN.",
            self.text_font,
            self.silver,
            self.panel.top + 160,
        )

        if self.refused:
            dialogue = (
                "DARLING. EVEN JESUS",
                "ONLY DID IT ONCE.",
                "HAVE SOME DIGNITY.",
            )
        else:
            dialogue = (
                "THE WIG IS CROOKED.",
                "THE HEELS ARE BROKEN.",
                "THE KINGDOM MOURNS.",
            )

        for index, line in enumerate(dialogue):
            self._draw_text(
                line,
                self.text_font,
                self.white,
                self.panel.top + 225 + index * 29,
            )

        if not self.refused:
            mercy_image = self.button_font.render(
                "BEG FOR MERCY",
                True,
                self.red,
            )
            mercy_position = mercy_image.get_rect(
                center=self.mercy_button.center
            )
            self.screen.blit(mercy_image, mercy_position)

        leave_image = self.button_font.render(
            "SASHAY AWAY",
            True,
            self.white,
        )
        leave_position = leave_image.get_rect(
            center=self.leave_button.center
        )
        self.screen.blit(leave_image, leave_position)

    def handle_event(
        self,
        event: pg.event.Event,
    ) -> GameOverAction | None:
        """Return the selected option for a left mouse click."""
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return None

        if self.leave_button.collidepoint(event.pos):
            return GameOverAction.SASHAY_AWAY

        if self.mercy_button.collidepoint(event.pos):
            if not self.refused:
                return GameOverAction.BEG_FOR_MERCY

        return None
