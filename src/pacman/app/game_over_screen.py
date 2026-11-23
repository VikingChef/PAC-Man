
"""Display the royal Game Over tribunal and its mercy choices."""

from enum import Enum, auto
from pathlib import Path

import pygame as pg
import time

from pacman.app.pause_menu import FONT_PATH
from pacman.app.ui_assets import IMAGES
from pacman.app.game_over_background import create_greyscale_background


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

        self.title_font = pg.font.Font(FONT_PATH, 18)
        self.text_font = pg.font.Font(FONT_PATH, 10)
        self.button_font = pg.font.Font(FONT_PATH, 11)

        self.white = (235, 230, 230)
        self.silver = (190, 190, 195)
        self.red = (210, 70, 80)

        self.refused = False
        self.background: pg.Surface | None = None

        self.original_background: pg.Surface | None = None
        self.fade_started_at: float | None = None

        # Position controls relative to the original artwork.
        screen_center = self.screen.get_rect().center
        self.panel = self.artwork.get_rect(
            center=(screen_center[0], screen_center[1] + 35)
        )

        self.mercy_button = pg.Rect(
            self.panel.left + 75,
            self.panel.top + 365,
            235,
            65,
        )
        self.leave_button = pg.Rect(
            self.panel.left + 340,
            self.panel.top + 365,
            235,
            65,
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
        position = (
            self.panel.centerx - image.get_width() // 2,
            center_y - image.get_height() // 2,
        )
        self.screen.blit(image, position)

    def render(self) -> None:
        """Render the frozen game and royal funeral tribunal."""

        if self.background is None:
            # Capture the final gameplay frame only once.
            self.original_background = self.screen.copy()
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
                # Keep the dark greyscale background permanently.
                self.background.set_alpha(None)
                self.screen.blit(self.background, (0, 0))
            else:
                # Fade only during the initial transition.
                opacity = int(progress * 255)
                fade_frame = self.background.copy()
                fade_frame.set_alpha(opacity)

                self.screen.blit(
                    self.original_background, (0, 0)
                )
                self.screen.blit(fade_frame, (0, 0))

        # The funeral artwork must retain its original colours.
        self.screen.blit(self.artwork, self.panel.topleft)

        self._draw_text(
            "GAME OVER, DARLING.",
            self.title_font,
            self.white,
            self.panel.top + 85,
        )

        self._draw_text(
            "A QUEEN HAS FALLEN.",
            self.text_font,
            self.silver,
            self.panel.top + 135,
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
                self.panel.top + 205 + index * 30,
            )

        # Remove the mercy label after the second plea.
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

        # Sashay Away remains available at all times.
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
