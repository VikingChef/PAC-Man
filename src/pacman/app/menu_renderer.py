
"""Render shared visual elements of the Pac-Man menus."""

import time

import pygame as pg

from pacman.app.actions import CharacterSelect, MainMenu
from pacman.app.highscore_select import HighScoreSelect
from pacman.app.viewport import fit_canvas, screen_to_canvas
from pacman.app.instructions_screen import InstructionsScreen


def background_frame_index(
    elapsed_ms: float,
    loaded_count: int,
    total_count: int,
) -> int:
    """Select a frame without wrapping within a growing frame list."""
    if loaded_count == 0 or total_count == 0:
        return 0

    # Use the fixed sequence length, not the number loaded so far.
    # If decoding falls behind, hold the latest available frame.
    intended_index = max(0, int(elapsed_ms) // 100) % total_count
    return min(intended_index, loaded_count - 1)


def render_menu_background(
    screen: pg.Surface,
    background_frames: list[pg.Surface],
    start_time: float,
    total_frame_count: int | None = None,
) -> None:
    """Draw available frames while the rest load progressively."""
    if not background_frames:
        screen.fill((0, 0, 0))
        return

    elapsed = time.time() * 1000 - start_time
    frame_index = background_frame_index(
        elapsed,
        len(background_frames),
        total_frame_count or len(background_frames),
    )

    # Backgrounds fill the screen, independently of menu scaling.
    background = pg.transform.scale(
        background_frames[frame_index],
        screen.get_size(),
    )
    screen.blit(background, (0, 0))


def render_menu_canvas(
    screen: pg.Surface,
    menu_canvas: pg.Surface,
) -> None:
    """Scale and centre the menu canvas on the physical display."""
    # Preserve the menu's proportions regardless of screen resolution.
    scale, (offset_x, offset_y) = fit_canvas(
        menu_canvas.get_size(),
        screen.get_size(),
    )

    scaled_size = (
        round(menu_canvas.get_width() * scale),
        round(menu_canvas.get_height() * scale),
    )

    # Keep the original smooth scaling used by both menus.
    scaled_menu = pg.transform.smoothscale(
        menu_canvas,
        scaled_size,
    )
    screen.blit(scaled_menu, (offset_x, offset_y))


def _prepare_menu(
    screen: pg.Surface,
    canvas: pg.Surface,
    background_frames: list[pg.Surface],
    start_time: float,
    total_frame_count: int | None = None,
) -> tuple[int, int]:
    """Draw the background and prepare mouse coordinates for a menu."""
    # Keep animation, canvas clearing and mouse scaling consistent.
    render_menu_background(
        screen,
        background_frames,
        start_time,
        total_frame_count,
    )
    canvas.fill((0, 0, 0, 0))

    mouse = screen_to_canvas(
        pg.mouse.get_pos(),
        canvas.get_size(),
        screen.get_size(),
    )

    # A pointer outside the fitted menu must not highlight a button.
    return mouse if mouse is not None else (-1, -1)


def render_main_menu(
    screen: pg.Surface,
    canvas: pg.Surface,
    background_frames: list[pg.Surface],
    start_time: float,
    menu: MainMenu,
    total_frame_count: int | None = None,
) -> None:
    """Present the animated main menu and its interactive buttons."""
    # Keep title animation and hover detection on one logical canvas.
    mouse = _prepare_menu(
        screen,
        canvas,
        background_frames,
        start_time,
        total_frame_count,
    )
    menu.render_main_menu(start_time, mouse, canvas)
    render_menu_canvas(screen, canvas)


def render_character_select(
    screen: pg.Surface,
    canvas: pg.Surface,
    background_frames: list[pg.Surface],
    start_time: float,
    menu: CharacterSelect,
    total_frame_count: int | None = None,
) -> None:
    """Present character selection with the shared menu background."""
    # Character artwork uses the same fitted canvas as the main menu.
    mouse = _prepare_menu(
        screen,
        canvas,
        background_frames,
        start_time,
        total_frame_count,
    )
    menu.render_char_select(mouse, canvas)
    render_menu_canvas(screen, canvas)


def render_highscore_select(
    screen: pg.Surface,
    canvas: pg.Surface,
    background_frames: list[pg.Surface],
    start_time: float,
    menu: HighScoreSelect,
    total_frame_count: int | None = None,
) -> None:
    """Present both halls over the existing animated background."""
    # Reuse the menu animation, mouse mapping and scaling pipeline.
    mouse = _prepare_menu(
        screen,
        canvas,
        background_frames,
        start_time,
        total_frame_count,
    )
    menu.render_highscore_select(mouse, canvas)
    render_menu_canvas(screen, canvas)


def render_instructions(
    screen: pg.Surface,
    canvas: pg.Surface,
    background_frames: list[pg.Surface],
    start_time: float,
    instructions: InstructionsScreen,
    total_frame_count: int | None = None,
) -> None:
    """Render scrollable instructions over the animated background."""
    mouse = _prepare_menu(
        screen,
        canvas,
        background_frames,
        start_time,
        total_frame_count,
    )
    instructions.render(mouse)
    render_menu_canvas(screen, canvas)
