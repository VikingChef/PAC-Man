
"""Display the DragViking Gaming startup logo."""

import time
from pathlib import Path

import pygame as pg

from pacman.app.ui_assets import IMAGES
from pacman.app.pixel_scaling import scale_pixels
from pacman.app.pixel_fading import blend_pixels


class StartupSplash:
    """Present a brief startup logo with fade transitions."""

    FADE_IN = 0.6
    HOLD = 1.8
    FADE_OUT = 0.6
    DURATION = FADE_IN + HOLD + FADE_OUT

    def __init__(self, screen: pg.Surface) -> None:
        """Load the logo and prepare its presentation."""
        self.screen = screen
        self.started_at = time.monotonic()

        image_path = Path(IMAGES) / "intro.jpeg"
        image = pg.image.load(str(image_path)).convert()

        # Preserve the logo's proportions on different displays.
        scale = min(
            screen.get_width() / image.get_width(),
            screen.get_height() / image.get_height(),
        )

        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale)),
        )

        self.logo = scale_pixels(image, size)
        self.logo_rect = self.logo.get_rect(
            center=screen.get_rect().center
        )
        # Reuse a black image as the starting point for the fade.
        self.black_logo = self.logo.copy()
        self.black_logo.fill((0, 0, 0))

    def finished(self, current_time: float) -> bool:
        """Report whether the startup presentation has ended."""
        return current_time - self.started_at >= self.DURATION

    def render(self, current_time: float) -> None:
        """Render the logo with a timed fade in and fade out."""
        elapsed = max(0.0, current_time - self.started_at)

        self.screen.fill((0, 0, 0))

        if elapsed >= self.DURATION:
            return

        if elapsed < self.FADE_IN:
            opacity = elapsed / self.FADE_IN
        elif elapsed < self.FADE_IN + self.HOLD:
            opacity = 1.0
        else:
            remaining = self.DURATION - elapsed
            opacity = remaining / self.FADE_OUT

        # Calculate the fade through direct pixel-buffer arithmetic.
        faded_logo = blend_pixels(
            self.black_logo,
            self.logo,
            max(0.0, min(1.0, opacity)),
        )

        self.screen.blit(faded_logo, self.logo_rect)
