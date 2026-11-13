
"""Tests for the mouse-operated Fabulous Control Panel."""

import pygame as pg
import pytest

from pacman.app.cheat_panel import CheatPanel
from pacman.game.cheat_mode import CheatMode


def test_clicking_fabulous_mode_activates_disco() -> None:
    """Verify that clicking Fabulous Mode activates disco mode."""

    # The panel needs Pygame's font system to create its labels.
    pg.font.init()

    # Create an off-screen surface so no game window is needed.
    screen = pg.Surface((1000, 800))

    # The panel controls the active CheatMode, not a separate copy.
    cheat_mode = CheatMode()
    panel = CheatPanel()

    # Use the panel's actual layout to locate the Fabulous Mode row.
    _, _, rows = panel._get_layout(screen)
    click_position = rows[0].center

    # Simulate clicking the first switch with the left mouse button.
    event = pg.event.Event(
        pg.MOUSEBUTTONDOWN,
        {"button": 1, "pos": click_position},
    )

    panel.handle_event(event, screen, cheat_mode)

    # The click should activate Fabulous Mode without marking cheating.
    assert cheat_mode.disco_enabled is True
    assert cheat_mode.cheats_used is False


@pytest.mark.parametrize(
    "row_index, attribute",
    [
        (1, "invincible"),
        (2, "ghosts_frozen"),
        (3, "timer_stopped"),
    ],
)
def test_clicking_gameplay_cheat_switches(
    row_index: int,
    attribute: str,
) -> None:
    """Verify that each gameplay switch changes the correct setting."""

    pg.font.init()

    screen = pg.Surface((1000, 800))
    cheat_mode = CheatMode()
    panel = CheatPanel()

    # Get the row corresponding to the cheat under test.
    _, _, rows = panel._get_layout(screen)

    event = pg.event.Event(
        pg.MOUSEBUTTONDOWN,
        {"button": 1, "pos": rows[row_index].center},
    )

    panel.handle_event(event, screen, cheat_mode)

    # Each switch must activate its corresponding cheat.
    assert getattr(cheat_mode, attribute) is True

    # Unlike Fabulous Mode, gameplay cheats invalidate a clean run.
    assert cheat_mode.cheats_used is True


def test_close_button_does_not_change_cheats() -> None:
    """Verify that closing the panel leaves cheat settings untouched."""

    pg.font.init()

    screen = pg.Surface((1000, 800))
    cheat_mode = CheatMode()
    panel = CheatPanel()

    # Locate the close button using the panel's own layout.
    _, close_button, _ = panel._get_layout(screen)

    event = pg.event.Event(
        pg.MOUSEBUTTONDOWN,
        {"button": 1, "pos": close_button.center},
    )

    # The panel reports a close request to the application.
    should_close = panel.handle_event(event, screen, cheat_mode)

    assert should_close is True

    # Closing the panel must not activate any gameplay cheats.
    assert cheat_mode.disco_enabled is False
    assert cheat_mode.invincible is False
    assert cheat_mode.ghosts_frozen is False
    assert cheat_mode.timer_stopped is False
    assert cheat_mode.cheats_used is False


@pytest.mark.parametrize(
    "event_type, button, position",
    [
        (pg.MOUSEBUTTONDOWN, 3, (500, 350)),
        (pg.MOUSEBUTTONDOWN, 1, (10, 10)),
        (pg.MOUSEMOTION, None, (500, 350)),
    ],
)
def test_unrelated_mouse_events_do_not_change_cheats(
    event_type: int,
    button: int | None,
    position: tuple[int, int],
) -> None:
    """Verify that unrelated mouse events leave the panel unchanged."""

    pg.font.init()

    screen = pg.Surface((1000, 800))
    cheat_mode = CheatMode()
    panel = CheatPanel()

    # Allow both mouse coordinates and integer button values.
    attributes: dict[str, tuple[int, int] | int] = {"pos": position}

    # Mouse motion events do not need a button attribute.
    if button is not None:
        attributes["button"] = button

    event = pg.event.Event(event_type, attributes)

    should_close = panel.handle_event(event, screen, cheat_mode)

    # Unrelated input must neither close the panel nor enable cheats.
    assert should_close is False
    assert cheat_mode.disco_enabled is False
    assert cheat_mode.invincible is False
    assert cheat_mode.ghosts_frozen is False
    assert cheat_mode.timer_stopped is False


@pytest.mark.parametrize("disco_enabled", [False, True])
def test_panel_renders_with_disco_states(
    disco_enabled: bool,
) -> None:
    """Verify the panel renders with Fabulous Mode on or off."""

    pg.font.init()

    screen = pg.Surface((1000, 800))
    cheat_mode = CheatMode()
    panel = CheatPanel()

    if disco_enabled:
        cheat_mode.toggle_disco_enabled()

    # Rendering should work regardless of the current cheat state.
    panel.render(screen, cheat_mode)

    # The panel should have drawn something onto the blank surface.
    panel_rectangle, _, _ = panel._get_layout(screen)
    assert screen.get_at(panel_rectangle.topleft)[:3] != (0, 0, 0)
