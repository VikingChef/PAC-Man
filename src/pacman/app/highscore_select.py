
"""Display the Hall of Fame and Hall of Shame selection menu."""

from enum import Enum, auto
from pathlib import Path

import pygame as pg

from pacman.app.ui_assets import IMAGES, center, load_trans_image
from pacman.app.ui_button import Button


FONT_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "PressStart2P-Regular.ttf"
)


class HighScoreSelectAction(Enum):
    """Identify the player's leaderboard selection."""

    HALL_OF_FAME = auto()
    HALL_OF_SHAME = auto()
    MAIN_MENU = auto()


class HighScoreSelect:
    """Present the two leaderboard choices using existing UI assets."""

    def __init__(self, screen: pg.Surface) -> None:
        """Load the selection artwork and prepare its buttons."""
        self.screen = screen
        width, height = screen.get_size()

        # Use Ilias's established 8-bit font for the heading.
        title_size = max(10, min(22, width // 40))
        self.title_font = pg.font.Font(str(FONT_PATH), title_size)

        # These images have no separate hover variants.
        # Build hover surfaces from the approved artwork itself.
        self.fame_button = Button(
            "hall_of_fame_menu.png",
            "hall_of_fame_menu.png",
            hover_offset=(0, 0),
        )
        self.shame_button = Button(
            "hall_of_shame_menu.png",
            "hall_of_shame_menu.png",
            hover_offset=(0, 0),
        )

        # Preserve the images' proportions and pixel-art appearance.
        button_width = int(width * 0.36)
        button_height = int(height * 0.34)

        self._prepare_button(
            self.fame_button,
            button_width,
            button_height,
        )
        self._prepare_button(
            self.shame_button,
            button_width,
            button_height,
        )

        # Position each choice within its half of the menu.
        fame_x = width // 4 - self.fame_button.width // 2
        shame_x = width * 3 // 4 - self.shame_button.width // 2

        fame_y = height // 2 - self.fame_button.height // 2
        shame_y = height // 2 - self.shame_button.height // 2

        self.fame_button.pos = (fame_x, fame_y)
        self.shame_button.pos = (shame_x, shame_y)

        self.buttons = (
            (self.fame_button, HighScoreSelectAction.HALL_OF_FAME),
            (self.shame_button, HighScoreSelectAction.HALL_OF_SHAME),
        )

        # Reuse the same Back button as Select Your Diva.
        self.back_button = Button(
            "go-back-symbol.png",
            "go-back-symbol-hover.png",
            pos=(0, height - 140),
            hover_offset=(-20, 50),
        )

        self.back_label = load_trans_image(
            f"{IMAGES}/back-to-main-menu.png"
        )
        self.back_label_pos = (10, height - 40)

    def _prepare_button(
        self,
        button: Button,
        maximum_width: int,
        maximum_height: int,
    ) -> None:
        """Fit artwork proportionally and create its hover image."""
        original_width, original_height = button.button.get_size()

        scale = min(
            maximum_width / original_width,
            maximum_height / original_height,
        )

        new_size = (
            max(1, round(original_width * scale)),
            max(1, round(original_height * scale)),
        )

        # Nearest-neighbour scaling preserves the pixel-art edges.
        button.button = pg.transform.scale(button.button, new_size)

        # Lighten the approved image rather than require new artwork.
        button.hover_button = button.button.copy()
        button.hover_button.fill(
            (30, 30, 30),
            special_flags=pg.BLEND_RGB_ADD,
        )

        # Button.hovering() uses these dimensions for hit detection.
        button.width, button.height = new_size

    def render_highscore_select(
        self,
        mouse_position: tuple[int, int],
        screen: pg.Surface,
    ) -> None:
        """Render the two choices and the established Back control."""
        mx, my = mouse_position

        title = self.title_font.render(
            "THE HALLS OF FAME & SHAME",
            True,
            "white",
        )
        title_pos = (
            center(screen.get_width(), title.get_width()),
            105,
        )
        screen.blit(title, title_pos)

        for button, _ in self.buttons:
            if button.hovering(mx, my):
                button.render_hover_button(screen)
            else:
                button.render_button(screen)

        if self.back_button.hovering(mx, my):
            self.back_button.render_hover_button(screen)
        else:
            self.back_button.render_button(screen)

        screen.blit(self.back_label, self.back_label_pos)

    def handle_event(
        self,
        event: pg.event.Event,
    ) -> HighScoreSelectAction | None:
        """Return the selected hall or Back to Main Menu."""
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return None

        mx, my = event.pos

        for button, action in self.buttons:
            if button.hovering(mx, my):
                return action

        if self.back_button.hovering(mx, my):
            return HighScoreSelectAction.MAIN_MENU

        return None
