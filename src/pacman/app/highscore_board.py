
"""Render the Hall of Fame and Hall of Shame leaderboards."""

from __future__ import annotations

from pathlib import Path

import pygame as pg

from pacman.app.pause_menu import FONT_PATH
from pacman.app.ui_assets import IMAGES, load_trans_image
from pacman.app.ui_button import Button
from pacman.game.highscores import HighScoreManager
from pacman.game.run_finalizer import EntryKind


class HighScoreBoard:
    """Display saved records over the approved leaderboard artwork."""

    def __init__(self, screen: pg.Surface) -> None:
        """Load both backgrounds and the existing Back button."""
        self.screen = screen
        self.width, self.height = screen.get_size()

        # Use the same pixel font throughout the game's menus.
        font_size = max(10, round(self.height * 0.018))
        title_size = max(14, round(self.height * 0.026))

        self.font = pg.font.Font(FONT_PATH, font_size)
        self.title_font = pg.font.Font(FONT_PATH, title_size)

        self.white = (255, 248, 230)
        self.gold = (255, 218, 110)
        self.pink = (255, 150, 195)

        # The illustrated backgrounds contain the scoreboard frames.
        self.fame_background = self._load_background(
            "hall_of_fame.png"
        )
        self.shame_background = self._load_background(
            "hall_of_shame.png"
        )

        # Reuse the Back control from Select Your Diva.
        self.back_button = Button(
            "go-back-symbol.png",
            "go-back-symbol-hover.png",
            pos=(0, self.height - 140),
            hover_offset=(-20, 50),
        )

        self.back_label = load_trans_image(
            f"{IMAGES}/back-to-main-menu.png"
        )

    def _load_background(self, filename: str) -> pg.Surface:
        """Fit approved artwork to the canvas without stretching it."""
        path = Path(IMAGES) / filename
        image = load_trans_image(str(path))

        image_width, image_height = image.get_size()

        # Both backgrounds have approximately 16:9 proportions.
        scale = min(
            self.width / image_width,
            self.height / image_height,
        )

        size = (
            max(1, round(image_width * scale)),
            max(1, round(image_height * scale)),
        )

        # Nearest-neighbour scaling preserves pixel-art styling.
        return pg.transform.scale(image, size)

    def _draw_background(self, kind: EntryKind) -> None:
        """Center the appropriate illustrated scoreboard."""
        self.screen.fill((0, 0, 0))

        image = (
            self.fame_background
            if kind == EntryKind.FAME
            else self.shame_background
        )

        position = (
            (self.width - image.get_width()) // 2,
            (self.height - image.get_height()) // 2,
        )
        self.screen.blit(image, position)

    def _draw_text(
        self,
        text: str,
        font: pg.font.Font,
        color: tuple[int, int, int],
        position: tuple[int, int],
        right_aligned: bool = False,
    ) -> None:
        """Draw pixel text with optional right alignment."""
        rendered = font.render(text, True, color)
        x, y = position

        if right_aligned:
            x -= rendered.get_width()

        self.screen.blit(rendered, (x, y))

    def _draw_title(
        self,
        text: str,
        color: tuple[int, int, int],
    ) -> None:
        """Center the leaderboard heading above its records."""
        rendered = self.title_font.render(text, True, color)

        position = (
            (self.width - rendered.get_width()) // 2,
            round(self.height * 0.17),
        )
        self.screen.blit(rendered, position)

    def _draw_fame(self, manager: HighScoreManager) -> None:
        """Display ten ranked initials and their scores."""
        self._draw_title("HALL OF FAME", self.gold)

        left = round(self.width * 0.26)
        right = round(self.width * 0.74)
        first_row = round(self.height * 0.26)
        row_spacing = round(self.height * 0.051)

        for index, entry in enumerate(manager.high_scores[:10]):
            y = first_row + index * row_spacing

            # The score column is aligned separately for readability.
            self._draw_text(
                f"{index + 1:02d}.  {entry.initials}",
                self.font,
                self.white,
                (left, y),
            )

            self._draw_text(
                f"{entry.score:,}",
                self.font,
                self.gold,
                (right, y),
                right_aligned=True,
            )

    def _draw_lips(self, x: int, y: int) -> None:
        """Draw a small pixel-style lipstick mark beside a cheater."""
        size = max(4, round(self.height * 0.008))

        # Two angular lips and a dark opening create a retro icon.
        upper = [
            (x - size * 2, y),
            (x - size, y - size),
            (x, y),
            (x + size, y - size),
            (x + size * 2, y),
        ]
        lower = [
            (x - size * 2, y),
            (x, y + size),
            (x + size * 2, y),
        ]

        pg.draw.polygon(self.screen, self.pink, upper)
        pg.draw.polygon(self.screen, self.pink, lower)

        pg.draw.line(
            self.screen,
            (90, 12, 48),
            (x - size, y),
            (x + size, y),
            max(1, size // 3),
        )

    def _draw_shame(self, manager: HighScoreManager) -> None:
        """Display the ten newest cheaters without deleting history."""
        self._draw_title("HALL OF SHAME", self.pink)

        left = round(self.width * 0.32)
        first_row = round(self.height * 0.26)
        row_spacing = round(self.height * 0.051)

        for index, entry in enumerate(
            manager.shame_manager.recent_cheaters()
        ):
            y = first_row + index * row_spacing

            # Each cheater receives a lipstick mark, not a score.
            self._draw_lips(
                left - round(self.width * 0.035),
                y + self.font.get_height() // 2,
            )

            self._draw_text(
                f"{index + 1:02d}.  {entry.name}",
                self.font,
                self.white,
                (left, y),
            )

    def _draw_back(
        self,
        mouse_position: tuple[int, int],
    ) -> None:
        """Display the established Back arrow and hover artwork."""
        mx, my = mouse_position

        if self.back_button.hovering(mx, my):
            self.back_button.render_hover_button(self.screen)
        else:
            self.back_button.render_button(self.screen)

        # Show the familiar label below the Back arrow.
        label_position = (
            10,
            self.height - 40,
        )
        self.screen.blit(self.back_label, label_position)

    def render(
        self,
        kind: EntryKind,
        manager: HighScoreManager,
        mouse_position: tuple[int, int],
    ) -> None:
        """Render the selected board and its navigation control."""
        self._draw_background(kind)

        if kind == EntryKind.FAME:
            self._draw_fame(manager)
        else:
            self._draw_shame(manager)

        self._draw_back(mouse_position)

    def handle_event(self, event: pg.event.Event) -> bool:
        """Report whether the player selected Back."""
        if event.type != pg.MOUSEBUTTONDOWN:
            return False

        if event.button != 1:
            return False

        return self.back_button.hovering(*event.pos)
