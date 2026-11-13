
"""Render gameplay information above the Pac-Man maze."""

import pygame as pg


FONT_PATH = "src/pacman/app/assets/PressStart2P-Regular.ttf"

LABEL_COLOR = (226, 165, 244)
VALUE_COLOR = (255, 255, 255)
CHEAT_COLOR = (255, 145, 210)
HEART_COLOR = (255, 90, 140)


class GameHUD:
    """Draw score, level, lives, timer and cheat acknowledgement."""

    def __init__(self) -> None:
        """Prepare fonts used by the gameplay HUD."""
        self.label_font = pg.font.Font(FONT_PATH, 20)
        self.value_font = pg.font.Font(FONT_PATH, 30)
        self.cheat_font = pg.font.Font(FONT_PATH, 17)

    def _draw_hearts(
        self,
        canvas: pg.Surface,
        centre_x: int,
        lives: int,
    ) -> None:
        """Draw one heart for each remaining life."""
        heart_spacing = 42

        # Centre the complete row, not each heart individually.
        # The row stays centred when the player loses a life.
        start_x = (
            centre_x - (lives - 1) * heart_spacing // 2
        )

        for index in range(lives):
            x = start_x + index * heart_spacing
            y = 57

            # Two overlapping circles form the top of the heart.
            pg.draw.circle(
                canvas,
                HEART_COLOR,
                (x - 7, y),
                9,
            )
            pg.draw.circle(
                canvas,
                HEART_COLOR,
                (x + 7, y),
                9,
            )

            # The triangle completes the pointed bottom.
            pg.draw.polygon(
                canvas,
                HEART_COLOR,
                [
                    (x - 16, y + 3),
                    (x + 16, y + 3),
                    (x, y + 23),
                ],
            )

    def render(
        self,
        canvas: pg.Surface,
        score: int,
        level: int,
        lives: int,
        remaining_time: int,
        cheats_used: bool,
    ) -> None:
        """Draw gameplay statistics and optional cheat acknowledgement."""
        column_width = canvas.get_width() // 4

        statistics = (
            ("SCORE", str(score)),
            ("LEVEL", str(level)),
            ("LIVES", ""),
            ("TIME", str(remaining_time)),
        )

        for index, (label, value) in enumerate(statistics):
            centre_x = column_width * index + column_width // 2

            label_surface = self.label_font.render(
                label,
                True,
                LABEL_COLOR,
            )
            label_rect = label_surface.get_rect(
                center=(centre_x, 25),
            )
            canvas.blit(label_surface, label_rect)

            # Lives are represented by hearts rather than a number.
            if label == "LIVES":
                self._draw_hearts(canvas, centre_x, lives)
                continue

            value_surface = self.value_font.render(
                value,
                True,
                VALUE_COLOR,
            )
            value_rect = value_surface.get_rect(
                center=(centre_x, 59),
            )
            canvas.blit(value_surface, value_rect)

        # Only actual cheating triggers the HUD acknowledgement.
        # Opening the panel or enabling Disco Mode alone does not.
        if cheats_used:
            message = self.cheat_font.render(
                "Oh honey, cheat much?",
                True,
                CHEAT_COLOR,
            )
            message_rect = message.get_rect(
                center=(canvas.get_width() // 2, 100),
            )
            canvas.blit(message, message_rect)
