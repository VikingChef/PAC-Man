
"""Handle application input and dispatch Pygame events."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pygame as pg

from pacman.app.actions import CharSelectAction, MainMenuAction
from pacman.app.viewport import screen_to_canvas

if TYPE_CHECKING:
    from pacman.app.application import AppState, PacManApp


def handle_events(
    app: PacManApp,
    states: type[AppState],
) -> None:
    """Dispatch input to the currently active interface."""
    for event in pg.event.get():
        # Window closure must work regardless of the current screen.
        if event.type == pg.QUIT:
            app.stop()
            continue

        # An open cheat panel captures input before the game or menus.
        # This prevents movement and menu actions behind the panel.
        if app.cheat_panel_open:
            _handle_cheat_panel_event(app, event)
            continue

        # Space switches between playing and the paused overlay.
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            if app.state == states.PLAYING:
                app.pause_game()
                continue
            if app.state == states.PAUSED:
                app.resume_game()
                continue

        # The pause menu captures clicks before ordinary gameplay input.
        if app.state == states.PAUSED:
            _handle_pause_event(app, event)
            continue

        # Outside the cheat panel, Escape closes the application.
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            app.stop()
            continue

        # Menu and character selection use their own input handlers.
        if app.state in (states.MAIN_MENU, states.CHAR_SELECT):
            _handle_menu_event(app, event, states)

        # Movement and cheat-code entry are gameplay-only actions.
        elif app.state == states.PLAYING:
            _handle_gameplay_event(app, event)


def _handle_cheat_panel_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Process input while the cheat panel is visible."""
    # Escape closes the panel instead of terminating the application.
    if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
        app.cheat_panel_open = False
        app.cheat_code.reset()
        return

    panel_event = event

    if event.type == pg.MOUSEBUTTONDOWN:
        # Mouse coordinates refer to the physical display, but panel
        # buttons are positioned on the logical gameplay canvas.
        canvas_position = screen_to_canvas(
            event.pos,
            app.display.game_canvas.get_size(),
            app.display.screen.get_size(),
        )

        # Ignore clicks outside the displayed gameplay canvas.
        if canvas_position is None:
            return

        # Preserve the original event data while replacing its position.
        panel_event = pg.event.Event(
            event.type,
            {**event.dict, "pos": canvas_position},
        )

    # The panel reports when an interaction should close it.
    if app.cheat_panel.handle_event(
        panel_event,
        app.display.game_canvas,
        app.cheat_mode,
    ):
        app.cheat_panel_open = False
        app.cheat_code.reset()


def _handle_menu_event(
    app: PacManApp,
    event: pg.event.Event,
    states: type[AppState],
) -> None:
    """Send menu input through logical canvas coordinates."""
    menu_event = event

    if event.type == pg.MOUSEBUTTONDOWN:
        # Menu buttons use logical canvas coordinates, not physical
        # screen coordinates. Convert clicks before hit detection.
        canvas_position = screen_to_canvas(
            event.pos,
            app.display.menu_canvas.get_size(),
            app.display.screen.get_size(),
        )

        # A click outside the menu canvas cannot select a button.
        if canvas_position is None:
            return

        # Keep the original event attributes apart from its position.
        menu_event = pg.event.Event(
            event.type,
            {**event.dict, "pos": canvas_position},
        )

    if app.state == states.MAIN_MENU:
        # The main menu returns an action; the application decides
        # which state transition that action should trigger.
        menu_action: MainMenuAction | None = (
            app.display.main_menu.handle_event(menu_event)
        )

        if menu_action is not None:
            app._handle_main_menu_action(menu_action)

    else:
        # Character selection follows the same event-to-action pattern,
        # keeping the UI separate from game initialization.
        character_action: CharSelectAction | None = (
            app.display.char_select.handle_event(menu_event)
        )

        if character_action is not None:
            app._handle_char_select_action(character_action)


def _handle_gameplay_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Process movement and the secret cheat sequence."""
    # Only key presses are relevant to gameplay controls here.
    if event.type != pg.KEYDOWN:
        return

    # Check the secret sequence before processing ordinary movement.
    # Timestamps allow the cheat-code handler to enforce its timing.
    unlocked = app.cheat_code.register_key(
        event.key,
        time.monotonic(),
    )

    if unlocked:
        # Opening the panel consumes this event, preventing movement
        # from occurring on the same key press.
        app.cheat_panel_open = True
        return

    # Translate supported keyboard keys into maze directions.
    # The application's key map handles arrow keys and WASD.
    if event.key in app.key_map:
        app.move_player(app.key_map[event.key])


def _handle_pause_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Route pause clicks through the scaled gameplay coordinates."""
    if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
        app.resume_game()
        return

    if event.type != pg.MOUSEBUTTONDOWN:
        return

    canvas_position = screen_to_canvas(
        event.pos,
        app.display.game_canvas.get_size(),
        app.display.screen.get_size(),
    )
    if canvas_position is None:
        return

    pause_event = pg.event.Event(
        event.type,
        {**event.dict, "pos": canvas_position},
    )
    selected_action = app.pause_menu.handle_event(pause_event)
    if selected_action is not None:
        app.handle_pause_action(selected_action)
