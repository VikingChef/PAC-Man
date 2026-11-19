
"""Display the royal proclamation with scrollable instructions."""

from pathlib import Path

import pygame as pg

from pacman.app.pause_menu import FONT_PATH
from pacman.app.ui_assets import IMAGES, load_trans_image
from pacman.app.ui_button import Button


INSTRUCTIONS = (
    (
        "A MOST SACRED PROCLAMATION",
        "Hear ye, hear ye, you magnificent creature!",
        "In an age of darkness, danger, and catastrophically "
        "poor fashion choices, the kingdom has summoned "
        "its greatest champion.",
        "You.",
        "Yes, you. Try to look surprised.",
        "Your destiny is to enter the cursed labyrinth, "
        "collect its fabulous riches, and emerge victorious.",
        "Preferably with your dignity intact.",
        "Although we make no promises.",
    ),
    (
        "THE UNINVITED GUESTS",
        "Four particularly dreadful spectres haunt these halls.",
        "Their resemblance to certain public figures is, "
        "of course, entirely coincidental.",
        "THE FIRST sports an extraordinary orange complexion, "
        "a suspicious golden hairstyle, and insists that "
        "this is the greatest maze ever built.",
        "He also claims to have won it already. Twice.",
        "THE SECOND is a self-proclaimed genius, "
        "obsessed with rockets, electric carriages, "
        "and purchasing things nobody wanted him to own.",
        "He believes every problem can be solved "
        "by firing someone.",
        "THE THIRD once enchanted an entire generation "
        "with tales of wizards and magical schools.",
        "These days, she seems considerably more interested "
        "in deciding who is allowed into the girls' "
        "dormitory.",
        "THE FOURTH campaigns fiercely against foreigners, "
        "while maintaining a rather international "
        "personal life herself.",
        "The irony, much like her sense of humour, "
        "appears to have escaped her.",
        "We shall name no names.",
        "The Royal Legal Department is already drinking.",
    ),
    (
        "THE ART OF MOVEMENT",
        "Must we really explain how the arrow keys work?",
        "Up goes up. Down goes down.",
        "Left and right are, astonishingly, left and right.",
        "Alternatively, use W, A, S, and D.",
        "W for up, A for left, S for down, D for right.",
        "Revolutionary technology, darling.",
        "Press SPACE to pause your adventure.",
        "Because even legends need a moment "
        "to adjust their wigs.",
    ),
    (
        "THE ROYAL OBJECTIVES",
        "Collect the money scattered throughout the maze.",
        "Every last delicious little morsel.",
        "Avoid the ghosts. Touching them is generally "
        "considered a poor life decision.",
        "Unless, of course, you have acquired "
        "a magnificent power pellet.",
        "These glorious treasures allow you to turn "
        "the tables upon your tormentors.",
        "For a brief moment, the hunted becomes "
        "the hunter.",
        "Enjoy it. It does not last forever.",
        "Clear the maze to continue your quest.",
    ),
    (
        "NO, SERIOUSLY",
        "Get the money and drag.",
        "Avoid the arseholes.",
        "Eat the power pellets.",
        "Chase the arseholes.",
        "Repeat.",
        "That's it.",
        "Honestly, what were you expecting?",
        "An undergraduate thesis?",
    ),
    (
        "FOR THE MORALLY FLEXIBLE",
        "There are whispers of a secret ritual.",
        "An ancient sequence, passed between "
        "generations of particularly naughty queens.",
        "Those who discover it may bend reality, "
        "mock the laws of nature, and become "
        "unreasonably fabulous.",
        "But consider this your warning:",
        "The Hall of Shame has an excellent memory.",
        "And absolutely no discretion.",
        "Now go forth, darling.",
        "BE GAY. DO CRIME. COLLECT COINS.",
    ),
)


class InstructionsScreen:
    """Render instructions inside a stationary illustrated scroll."""

    def __init__(self, screen: pg.Surface) -> None:
        """Prepare scroll artwork, text and navigation."""
        self.screen = screen
        width, height = screen.get_size()

        scroll_path = Path(IMAGES) / "Instruction_scroll.png"
        image = load_trans_image(str(scroll_path))

        scale = min(
            height * 0.88 / image.get_height(),
            width * 0.72 / image.get_width(),
        )
        scroll_size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale)),
        )

        self.scroll = pg.transform.scale(image, scroll_size)
        self.scroll_rect = self.scroll.get_rect(
            center=(width // 2, height // 2)
        )

        # Keep text inside the parchment, away from the rollers.
        self.text_rect = pg.Rect(
            self.scroll_rect.x + round(scroll_size[0] * 0.20),
            self.scroll_rect.y + round(scroll_size[1] * 0.14),
            round(scroll_size[0] * 0.60),
            round(scroll_size[1] * 0.72),
        )

        font_size = max(9, round(height * 0.013))
        heading_size = max(11, round(height * 0.015))

        self.font = pg.font.Font(FONT_PATH, font_size)
        self.heading_font = pg.font.Font(
            FONT_PATH,
            heading_size,
        )

        self.ink_color = (77, 44, 27)
        self.heading_color = (112, 45, 29)

        self.line_spacing = max(5, font_size // 2)
        self.paragraph_spacing = font_size
        self.section_spacing = font_size * 2

        self.lines: list[
            tuple[pg.Surface, int, bool]
        ] = []

        self.content_height = 0
        self.scroll_offset = 0
        self.scroll_step = max(24, font_size * 3)

        self._prepare_text()

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

    def _wrap_text(
        self,
        text: str,
        font: pg.font.Font,
    ) -> list[str]:
        """Wrap words to fit within the parchment writing area."""
        words = text.split()
        lines: list[str] = []
        current = ""

        for word in words:
            candidate = f"{current} {word}".strip()

            if font.size(candidate)[0] <= self.text_rect.width:
                current = candidate
                continue

            if current:
                lines.append(current)
                current = ""

            # Handle exceptionally long words without overflowing.
            for character in word:
                candidate = current + character

                if (
                    current
                    and font.size(candidate)[0]
                    > self.text_rect.width
                ):
                    lines.append(current)
                    current = character
                else:
                    current = candidate

        if current:
            lines.append(current)

        return lines

    def _prepare_text(self) -> None:
        """Pre-render wrapped text for efficient scrolling."""
        cursor = 0

        for section in INSTRUCTIONS:
            heading, *paragraphs = section

            for line in self._wrap_text(
                heading,
                self.heading_font,
            ):
                rendered = self.heading_font.render(
                    line,
                    False,
                    self.heading_color,
                )
                self.lines.append((rendered, cursor, True))
                cursor += (
                    self.heading_font.get_linesize()
                    + self.line_spacing
                )

            cursor += self.section_spacing

            for paragraph in paragraphs:
                for line in self._wrap_text(
                    paragraph,
                    self.font,
                ):
                    rendered = self.font.render(
                        line,
                        False,
                        self.ink_color,
                    )
                    self.lines.append((rendered, cursor, False))
                    cursor += (
                        self.font.get_linesize()
                        + self.line_spacing
                    )

                cursor += self.paragraph_spacing

            cursor += self.section_spacing

        self.content_height = cursor

    def _scroll_by(self, amount: int) -> None:
        """Move the text without exposing empty space at the end."""
        maximum = max(
            0,
            self.content_height - self.text_rect.height,
        )
        self.scroll_offset = max(
            0,
            min(maximum, self.scroll_offset + amount),
        )

    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle scrolling and report whether Back was selected."""
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return True

            if event.key == pg.K_DOWN:
                self._scroll_by(self.scroll_step)
            elif event.key == pg.K_UP:
                self._scroll_by(-self.scroll_step)
            elif event.key == pg.K_PAGEDOWN:
                self._scroll_by(self.text_rect.height)
            elif event.key == pg.K_PAGEUP:
                self._scroll_by(-self.text_rect.height)
            elif event.key == pg.K_HOME:
                self.scroll_offset = 0
            elif event.key == pg.K_END:
                self._scroll_by(self.content_height)

        elif event.type == pg.MOUSEWHEEL:
            self._scroll_by(-event.y * self.scroll_step)

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:
                self._scroll_by(-self.scroll_step)
            elif event.button == 5:
                self._scroll_by(self.scroll_step)
            elif event.button == 1:
                return self.back_button.hovering(*event.pos)

        return False

    def _render_text(self) -> None:
        """Clip moving text to the parchment writing area."""
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(self.text_rect)

        for rendered, line_y, is_heading in self.lines:
            y = (
                self.text_rect.y
                + line_y
                - self.scroll_offset
            )

            if y + rendered.get_height() <= self.text_rect.top:
                continue

            if y >= self.text_rect.bottom:
                continue

            x = self.text_rect.x

            if is_heading:
                x += (
                    self.text_rect.width
                    - rendered.get_width()
                ) // 2

            self.screen.blit(rendered, (x, y))

        self.screen.set_clip(previous_clip)

    def render(
        self,
        mouse_position: tuple[int, int],
    ) -> None:
        """Draw the parchment, moving text and established Back UI."""
        self.screen.blit(self.scroll, self.scroll_rect)
        self._render_text()

        if self.back_button.hovering(*mouse_position):
            self.back_button.render_hover_button(self.screen)
        else:
            self.back_button.render_button(self.screen)

        self.screen.blit(
            self.back_label,
            self.back_label_pos,
        )
