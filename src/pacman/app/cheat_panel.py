
"""Mouse-operated cheat control panel for Pac-Man.

The panel manages presentation and mouse interaction only.
The active CheatMode object remains responsible for cheat behaviour.
"""

import pygame as pg

from pacman.game.cheat_mode import CheatMode


class CheatPanel:
    """Draw and operate the Fabulous Control Panel.

    The application owns whether the panel is open and whether gameplay
    is paused. This class only displays the available cheats and
    forwards mouse clicks to the existing CheatMode toggle methods.

    CheatMode is passed to each operation instead of being stored.
    This prevents stale references when a new game resets cheat state.
    """

    # Keep the display order consistent with the switch behaviour.
    CHEAT_LABELS = (
        "Fabulous Mode",
        "Invincibility",
        "Ghost Freeze",
        "Timer Freeze",
    )

    # Colours are centralised so the visual theme is easy to adjust.
    BACKGROUND = (36, 20, 55)
    BORDER = (235, 125, 225)
    TEXT = (250, 240, 255)
    MUTED_TEXT = (190, 175, 205)
    ROW_BACKGROUND = (58, 39, 78)
    SWITCH_ON = (110, 225, 170)
    SWITCH_OFF = (115, 100, 135)
    SWITCH_KNOB = (255, 255, 255)

    def __init__(self) -> None:
        """Prepare retro pixel fonts for the control panel."""
        font_path = "src/pacman/app/assets/PressStart2P-Regular.ttf"

        # Pixel fonts are wider than Arial, so use smaller sizes.
        self.title_font = pg.font.Font(font_path, 24)
        self.label_font = pg.font.Font(font_path, 15)
        self.detail_font = pg.font.Font(font_path, 12)

    def _get_layout(
        self,
        screen: pg.Surface,
    ) -> tuple[pg.Rect, pg.Rect, list[pg.Rect]]:
        """Calculate the panel, close button and cheat row positions.

        Drawing and mouse handling share this layout. Consequently,
        the clickable areas always match the visible controls.
        """
        screen_width, screen_height = screen.get_size()

        panel_width = min(640, screen_width - 32)
        panel_height = min(470, screen_height - 32)

        panel = pg.Rect(0, 0, panel_width, panel_height)
        panel.center = (screen_width // 2, screen_height // 2)

        close_button = pg.Rect(
            panel.right - 52,
            panel.top + 15,
            34,
            34,
        )

        # All four controls use the same spacing and dimensions.
        row_width = panel.width - 60
        row_height = 58
        row_spacing = 12
        # Leave room for a two-line title and its subtitle.
        first_row_y = panel.top + 140

        rows = [
            pg.Rect(
                panel.left + 30,
                first_row_y + index * (row_height + row_spacing),
                row_width,
                row_height,
            )
            for index in range(len(self.CHEAT_LABELS))
        ]

        return panel, close_button, rows

    def handle_event(
        self,
        event: pg.event.Event,
        screen: pg.Surface,
        cheat_mode: CheatMode,
    ) -> bool:
        """Handle a mouse click on the panel.

        Args:
            event: The Pygame event being processed.
            screen: The display surface used to calculate hitboxes.
            cheat_mode: The active game's cheat settings.

        Returns:
            True if the close button was clicked, otherwise False.

        Clicking a switch changes its associated CheatMode setting.
        The application remains responsible for closing the panel.
        """
        if event.type != pg.MOUSEBUTTONDOWN:
            return False

        # Only the primary mouse button operates the controls.
        if event.button != 1:
            return False

        _, close_button, rows = self._get_layout(screen)

        if close_button.collidepoint(event.pos):
            return True

        for index, row in enumerate(rows):
            if not row.collidepoint(event.pos):
                continue

            # Reuse the gameplay methods instead of duplicating logic.
            if index == 0:
                cheat_mode.toggle_disco_enabled()
            elif index == 1:
                cheat_mode.toggle_invincibility()
            elif index == 2:
                cheat_mode.toggle_ghost_freeze()
            elif index == 3:
                cheat_mode.toggle_timer_stopped()

            # A click should operate only one switch.
            break

        return False

    def render(
        self,
        screen: pg.Surface,
        cheat_mode: CheatMode,
    ) -> None:
        """Draw the panel using the current cheat settings.

        The overlay darkens the game without modifying the underlying
        game surface or changing any gameplay state.
        """
        panel, close_button, rows = self._get_layout(screen)

        # A transparent overlay keeps the paused maze visible behind
        # the menu while making the controls easier to read.
        overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
        overlay.fill((10, 5, 20, 190))
        screen.blit(overlay, (0, 0))

        pg.draw.rect(
            screen,
            self.BACKGROUND,
            panel,
            border_radius=18,
        )
        pg.draw.rect(
            screen,
            self.BORDER,
            panel,
            width=3,
            border_radius=18,
        )

        # Split the title into two centred lines to avoid the X.
        title_lines = (
            "THE FABULOUS",
            "CONTROL PANEL",
        )

        for index, line in enumerate(title_lines):
            title = self.title_font.render(
                line,
                True,
                self.TEXT,
            )
            title_rect = title.get_rect(
                center=(
                    panel.centerx,
                    panel.top + 35 + index * 38,
                ),
            )
            screen.blit(title, title_rect)

        subtitle = self.detail_font.render(
            "Darling, choose your superpowers.",
            True,
            self.MUTED_TEXT,
        )
        screen.blit(
            subtitle,
            (panel.centerx - subtitle.get_width() // 2, panel.top + 105),
        )

        # The states are read directly from CheatMode on every frame.
        # This keeps the displayed switches synchronised with gameplay.
        cheat_states = (
            cheat_mode.disco_enabled,
            cheat_mode.invincible,
            cheat_mode.ghosts_frozen,
            cheat_mode.timer_stopped,
        )

        for label, enabled, row in zip(
            self.CHEAT_LABELS,
            cheat_states,
            rows,
        ):
            pg.draw.rect(
                screen,
                self.ROW_BACKGROUND,
                row,
                border_radius=12,
            )

            label_surface = self.label_font.render(
                label,
                True,
                self.TEXT,
            )
            screen.blit(
                label_surface,
                (
                    row.left + 18,
                    row.centery - label_surface.get_height() // 2,
                ),
            )

            # Represent each cheat as a familiar sliding switch.
            switch = pg.Rect(
                row.right - 84,
                row.centery - 15,
                65,
                30,
            )

            switch_colour = (
                self.SWITCH_ON if enabled else self.SWITCH_OFF
            )
            pg.draw.rect(
                screen,
                switch_colour,
                switch,
                border_radius=15,
            )

            # Move the knob to the right when the setting is enabled.
            knob_x = switch.right - 16 if enabled else switch.left + 16
            pg.draw.circle(
                screen,
                self.SWITCH_KNOB,
                (knob_x, switch.centery),
                12,
            )

        # Provide a visible mouse target for closing the menu.
        pg.draw.rect(
            screen,
            self.ROW_BACKGROUND,
            close_button,
            border_radius=8,
        )
        close_text = self.label_font.render(
            "X",
            True,
            self.TEXT,
        )
        screen.blit(
            close_text,
            close_text.get_rect(center=close_button.center),
        )

        footer = self.detail_font.render(
            "ESC to close and return to the maze",
            True,
            self.MUTED_TEXT,
        )
        screen.blit(
            footer,
            (
                panel.centerx - footer.get_width() // 2,
                panel.bottom - 35,
            ),
        )
