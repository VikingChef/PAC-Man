
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
        "Yes, you. Try to keep up...",
        "Your destiny is to enter the cursed labyrinth, "
        "relieve it of its riches, and emerge victorious.",
        "Ideally with your dignity intact.",
        "Your wig, however, is entirely your OWN responsibility.",
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
        "THE FOURTH is a self-styled Germanic imperialist "
        "who believes her country has far too many foreigners.",
        "Despite sharing her life with a woman of foreign "
        "descent, she champions a party opposed to "
        "same-sex marriage and immigration.",
        "Apparently, equality and diversity are wonderful "
        "things, provided they stay within her own household.",
        "We shall name no names.",
        "The Royal Legal Department has strongly advised "
        "against it.",
        "Their objections were delivered in writing, "
        "followed by several increasingly desperate "
        "phone calls.",
        "The Head of Legal has since retreated "
        "to a fortified wine cellar.",
        "We are told negotiations with a second bottle "
        "are progressing well.",
        "No further statements will be issued.",
    ),
    (
        "THE ART OF MOVEMENT",
        "Before embarking upon your glorious quest, "
        "we must address the delicate matter of locomotion.",
        "Do you genuinely need to be told how the arrow "
        "keys work?",
        "Very well.",
        "UP moves you up. DOWN moves you down.",
        "LEFT and RIGHT are, astonishingly, left and right.",
        "For those who consider themselves technologically "
        "sophisticated, there is also W, A, S and D.",
        "W goes up. A goes left. S goes down. D goes right.",
        "Yes, darling. It's exactly the same thing, "
        "but with letters.",
        "Should the overwhelming complexity of four "
        "directions become too much, press SPACE to pause.",
        "Take a moment. Question your life choices.",
        "We shall endeavour not to judge.",
        "At least, not to your face.",
        "And when you're ready?",
        "Sniff some poppers, fix your tuck, wig and mug, and...",
        "GIVE THEM HELL!!!",
    ),
    (
        "THE ROYAL OBJECTIVES",
        "Your Majesty, the labyrinth is positively "
        "overflowing with riches.",
        "Naturally, they belong to you.",
        "Collect every last coin. Consider it a "
        "redistribution of wealth, with considerably "
        "better accessories.",
        "Unfortunately, four thoroughly objectionable "
        "spectres have taken it upon themselves to "
        "interfere with your financial ambitions.",
        "Avoid them. They have no respect for personal "
        "space, and physical contact may prove fatal.",
        "To your dignity, amongst other things.",
        "But fear not! Scattered throughout the labyrinth "
        "are magnificent doses of DRAG.",
        "Collect one, and for a brief, glorious moment, "
        "the tables are turned.",
        "The hunted becomes the hunter.",
        "The bullies become the bullied.",
        "And the arseholes become considerably more nervous.",
        "But remember, darling: DRAG DOESN'T LAST FOREVER.",
        "Once its magic fades, those dreadful creatures "
        "will resume their pursuit.",
        "Collect all the money, survive their nonsense, "
        "and advance to the next labyrinth.",
        "Do try not to die. The paperwork is simply exhausting.",
    ),
    (
        "NO, SERIOUSLY",
        "Get the money.",
        "Avoid the arseholes.",
        "Get the drag.",
        "And when you've got drag?",
        "CLOCK THE BASTARDS TO THEIR FACE!",
        "Repeat.",
        "That's it.",
        "Honestly, what were you expecting?",
        "An undergraduate thesis?",
    ),
    (
        "FOR THE MORALLY FLEXIBLE",
        "There are whispers of a secret ritual.",
        "An ancient sequence, passed from queen to queen, "
        "whispered in dressing rooms and scratched into "
        "the walls of particularly disreputable establishments.",
        "Those who master it may bend reality, silence "
        "their enemies, and acquire powers that would "
        "make the gods themselves question their career choices.",
        "But how does one invoke such fabulous heresy?",
        "The old queens speak of a dance.",
        "First, one must rise to greatness.",
        "Then rise again, for once is never enough.",
        "What goes up must come down.",
        "And down again, because a good whore knows "
        "that enthusiasm is a virtue, not a vice.",
        "From there, the path takes an unexpected turn.",
        "And one unexpected turn deserves another.",
        "And from there, darling, you must SEE.",
        "But remember, darling, forbidden magic is not "
        "performed from the comfort of a reading room.",
        "One must enter the labyrinth before "
        "attempting the ritual.",
        "Beware: those who invoke forbidden powers "
        "may find their names immortalised "
        "in the Hall of Shame.",
        "The Royal Legal Department declines to comment.",
        "They are still in the wine cellar.",
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
