
"""Handle application input and dispatch Pygame events."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pygame as pg

from pacman.app.actions import CharSelectAction, MainMenuAction
from pacman.app.name_entry import NameEntryAction
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

        # Name entry captures input before global keyboard shortcuts.
        if app.state == states.NAME_ENTRY:
            _handle_name_entry_event(app, event)
            continue

        # An open cheat panel captures input before ordinary gameplay.
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

        # The pause menu captures input before ordinary gameplay.
        if app.state == states.PAUSED:
            _handle_pause_event(app, event)
            continue

        # The royal tribunal captures input before global shortcuts.
        if app.state == states.GAME_OVER:
            _handle_game_over_event(app, event)
            continue

        # High-score screens own their Back and selection controls.
        if app.state == states.HIGHSCORES:
            _handle_highscores_event(app, event)
            continue

        if app.state == states.INSTRUCTIONS:
            _handle_instructions_event(app, event)
            continue

        # Escape closes the application outside special interfaces.
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            app.stop()
            continue

        # Main menu and character selection use their own handlers.
        if app.state in (states.MAIN_MENU, states.CHAR_SELECT):
            _handle_menu_event(app, event, states)

        # Movement and cheat codes are gameplay-only actions.
        elif app.state == states.PLAYING:
            _handle_gameplay_event(app, event)

        elif app.state == states.VICTORY:
            # Handle the player's exit from the victory celebration.
            _handle_victory_event(app, event)


def _handle_name_entry_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Route name entry through the logical menu canvas."""
    name_event = event

    if event.type == pg.MOUSEBUTTONDOWN:
        canvas_position = screen_to_canvas(
            event.pos,
            app.display.menu_canvas.get_size(),
            app.display.screen.get_size(),
        )

        if canvas_position is None:
            return

        name_event = pg.event.Event(
            event.type,
            {**event.dict, "pos": canvas_position},
        )

    action: NameEntryAction | None = (
        app.name_entry.handle_event(name_event)
    )

    if action is not None:
        app.handle_name_entry_action(action)


def _handle_instructions_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Handle scrolling and navigation in the instructions menu."""
    instruction_event = event

    if event.type == pg.MOUSEBUTTONDOWN:
        canvas_position = screen_to_canvas(
            event.pos,
            app.display.menu_canvas.get_size(),
            app.display.screen.get_size(),
        )

        if canvas_position is None:
            return

        instruction_event = pg.event.Event(
            event.type,
            {**event.dict, "pos": canvas_position},
        )

    if app.instructions_screen.handle_event(instruction_event):
        app.change_state(type(app.state).MAIN_MENU)


def _handle_highscores_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Route leaderboard navigation through menu coordinates."""
    menu_event = event

    if event.type == pg.MOUSEBUTTONDOWN:
        canvas_position = screen_to_canvas(
            event.pos,
            app.display.menu_canvas.get_size(),
            app.display.screen.get_size(),
        )

        # Ignore clicks outside the displayed menu canvas.
        if canvas_position is None:
            return

        menu_event = pg.event.Event(
            event.type,
            {**event.dict, "pos": canvas_position},
        )

    # The app decides whether selection or a board is visible.
    app.handle_highscores_event(menu_event)


def _handle_cheat_panel_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Process input while the cheat panel is visible."""
    # Escape closes the panel instead of terminating the game.
    if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
        app.cheat_panel_open = False
        app.cheat_code.reset()
        return

    panel_event = event

    if event.type == pg.MOUSEBUTTONDOWN:
        # Convert physical coordinates to the gameplay canvas.
        canvas_position = screen_to_canvas(
            event.pos,
            app.display.game_canvas.get_size(),
            app.display.screen.get_size(),
        )

        if canvas_position is None:
            return

        panel_event = pg.event.Event(
            event.type,
            {**event.dict, "pos": canvas_position},
        )

    # The panel reports whether interaction should close it.
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
        # Convert screen clicks to the logical menu canvas.
        canvas_position = screen_to_canvas(
            event.pos,
            app.display.menu_canvas.get_size(),
            app.display.screen.get_size(),
        )

        if canvas_position is None:
            return

        menu_event = pg.event.Event(
            event.type,
            {**event.dict, "pos": canvas_position},
        )

    if app.state == states.MAIN_MENU:
        menu_action: MainMenuAction | None = (
            app.display.main_menu.handle_event(menu_event)
        )

        if menu_action is not None:
            app._handle_main_menu_action(menu_action)

    else:
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
    if event.type != pg.KEYDOWN:
        return

    # Temporary development shortcut for testing the victory screen.
    if event.key == pg.K_BACKSPACE:
        from pacman.app.application import AppState
        app.change_state(AppState.VICTORY)
        return

    # Check the secret sequence before ordinary movement.
    unlocked = app.cheat_code.register_key(
        event.key,
        time.monotonic(),
    )

    if unlocked:
        app.cheat_panel_open = True
        return

    # Translate supported keys into maze directions.
    if event.key in app.key_map:
        app.move_player(app.key_map[event.key])


def _handle_pause_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Route pause clicks through scaled gameplay coordinates."""
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


def _handle_game_over_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Route royal tribunal clicks through gameplay coordinates."""
    if event.type != pg.MOUSEBUTTONDOWN:
        return

    canvas_position = screen_to_canvas(
        event.pos,
        app.display.game_canvas.get_size(),
        app.display.screen.get_size(),
    )

    if canvas_position is None:
        return

    game_over_event = pg.event.Event(
        event.type,
        {**event.dict, "pos": canvas_position},
    )

    action = app.game_over_screen.handle_event(game_over_event)

    if action is not None:
        app.handle_game_over_action(action)


def _handle_victory_event(
    app: PacManApp,
    event: pg.event.Event,
) -> None:
    """Handle the player's choice to leave the victory screen."""
    # Only respond to the primary mouse button being pressed.
    if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
        return

    # The victory screen owns its button's position on the display.
    if not app.victory_screen.hover.collidepoint(event.pos):
        return

    # Qualifying scores open name entry; all others return to the menu.
    if not app._finalize_run():
        from pacman.app.application import AppState

        app.change_state(AppState.MAIN_MENU)
