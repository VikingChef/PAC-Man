
"""Present the active application screen and its overlays."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pacman.app.viewport import render_canvas

if TYPE_CHECKING:
    from pacman.app.application import AppState, PacManApp


def render_current_frame(
    app: PacManApp,
    states: type[AppState],
    current_time: float,
) -> None:
    """Draw the current application state and its overlays."""
    if app.state == states.MAIN_MENU:
        app._run_main_menu()

    elif app.state == states.CHAR_SELECT:
        app._run_char_select()

    elif app.state == states.PLAYING:
        app._run_game()

    elif app.state == states.DYING:
        _render_dying(app, current_time)

    elif app.state == states.PAUSED:
        app._run_pause_menu()

    elif app.state == states.TIMEOUT:
        _render_timeout(app, states, current_time)

    elif app.state == states.GAME_OVER:
        app._run_game_over()

    elif app.state == states.VICTORY:
        app._run_victory()

    elif app.state == states.NAME_ENTRY:
        app._run_name_entry()

    elif app.state == states.HIGHSCORES:
        app._run_highscores()

    elif app.state == states.INSTRUCTIONS:
        app._run_instructions()

    _render_overlays(app, states)


def _render_dying(
    app: PacManApp,
    current_time: float,
) -> None:
    """Show the collision before resolving the lost life."""
    if (
        app.death_started_at is not None
        and current_time - app.death_started_at >= 0.35
    ):
        app._finish_death()

    # Preserve the original collision rendering behaviour.
    app._run_game()


def _render_timeout(
    app: PacManApp,
    states: type[AppState],
    current_time: float,
) -> None:
    """Show the expired level before resolving the timeout."""
    if (
        app.timeout_started_at is not None
        and current_time - app.timeout_started_at >= 3.0
    ):
        app._finish_timeout()
    else:
        app._run_game()


def _render_overlays(
    app: PacManApp,
    states: type[AppState],
) -> None:
    """Draw gameplay overlays and scale the game canvas."""
    if (
        app.cheat_panel_open
        and app.state == states.PLAYING
    ):
        app.cheat_panel.render(
            app.display.game_canvas,
            app.cheat_mode,
        )

    if app.state in (
        states.PLAYING,
        states.PAUSED,
        states.DYING,
        states.TIMEOUT,
    ):
        render_canvas(
            app.display.game_canvas,
            app.display.screen,
        )
