
"""Tests for the gameplay HUD."""

import pygame as pg

from pacman.app.hud import GameHUD


BACKGROUND = (24, 18, 38)


def count_changed_pixels(
    surface: pg.Surface,
    area: pg.Rect,
) -> int:
    """Count pixels that differ from the background colour."""
    changed = 0

    # Inspect only the relevant area instead of the entire canvas.
    for y in range(area.top, area.bottom):
        for x in range(area.left, area.right):
            if surface.get_at((x, y))[:3] != BACKGROUND:
                changed += 1

    return changed


def test_hud_renders_game_statistics() -> None:
    """Verify that the HUD draws its four statistics."""
    pg.init()

    canvas = pg.Surface((1920, 1440))
    canvas.fill(BACKGROUND)

    hud = GameHUD()
    hud.render(
        canvas,
        score=1250,
        level=2,
        lives=3,
        remaining_time=78,
        cheats_used=False,
    )

    # Each of the four columns should contain rendered text.
    for column in range(4):
        area = pg.Rect(column * 480, 0, 480, 80)
        assert count_changed_pixels(canvas, area) > 0


def test_hud_shows_message_only_after_cheating() -> None:
    """Verify that cheating controls the HUD acknowledgement."""
    pg.init()

    hud = GameHUD()

    clean_canvas = pg.Surface((1920, 1440))
    cheated_canvas = pg.Surface((1920, 1440))

    clean_canvas.fill(BACKGROUND)
    cheated_canvas.fill(BACKGROUND)

    hud.render(clean_canvas, 100, 1, 3, 80, False)
    hud.render(cheated_canvas, 100, 1, 3, 80, True)

    # The message occupies the area below the four statistics.
    message_area = pg.Rect(500, 85, 920, 30)

    # Normal gameplay must leave this area completely untouched.
    assert count_changed_pixels(clean_canvas, message_area) == 0

    # Actual cheating must display the pink acknowledgement.
    assert count_changed_pixels(cheated_canvas, message_area) > 0


def test_hud_displays_one_heart_per_life() -> None:
    """Verify the number of visible hearts follows remaining lives."""
    pg.init()
    hud = GameHUD()

    def heart_pixels(lives: int) -> int:
        """Count rendered pixels in the heart display area."""
        canvas = pg.Surface((1920, 1440))
        canvas.fill(BACKGROUND)

        hud.render(canvas, 100, 1, lives, 80, False)

        # The lives column is the third of four HUD columns.
        # This area sits below its label, where hearts will appear.
        heart_area = pg.Rect(960, 43, 480, 42)
        return count_changed_pixels(canvas, heart_area)

    assert heart_pixels(0) == 0
    assert heart_pixels(1) > 0
    assert heart_pixels(2) > heart_pixels(1)
    assert heart_pixels(3) > heart_pixels(2)
