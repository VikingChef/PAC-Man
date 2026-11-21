
"""Render the maze and active Pac-Man gameplay."""

import time
from collections.abc import Callable

import pygame as pg

from pacman.app.disco_effects import DiscoEffects
from pacman.app.hud import GameHUD
from pacman.app.sprite_animator import SpriteAnimator
from pacman.game.cheat_mode import CheatMode
from pacman.game.level import Level
from pacman.game.state import GameState
from pacman.app.actions import center


CellPosition = tuple[int, int]
BlockPositions = list[list[CellPosition]]
SpritePosition = Callable[
    [CellPosition, CellPosition],
    CellPosition,
]


def render_maze_walls(
    canvas: pg.Surface,
    wall_sprite: pg.Surface,
    maze_layout: list[list[str]],
    block_positions: BlockPositions,
) -> None:
    """Draw maze walls at their calculated visual positions."""
    for row_index, row in enumerate(maze_layout):
        for column_index, cell in enumerate(row):
            if cell != "wall":
                continue

            canvas.blit(
                wall_sprite,
                block_positions[row_index][column_index],
            )


def render_disco_effects(
    canvas: pg.Surface,
    block_positions: BlockPositions,
    wall_sprite: pg.Surface,
    disco_effects: DiscoEffects,
) -> None:
    """Draw disco lighting across the complete maze."""
    if not block_positions:
        return

    maze_left, maze_top = block_positions[0][0]
    last_x, last_y = block_positions[-1][-1]

    maze_bounds = pg.Rect(
        maze_left,
        maze_top,
        last_x + wall_sprite.get_width() - maze_left,
        last_y + wall_sprite.get_height() - maze_top,
    )

    disco_effects.render(
        canvas,
        maze_bounds,
        time.monotonic(),
    )


def render_player(
    canvas: pg.Surface,
    level: Level,
    sprite_position: SpritePosition,
) -> None:
    """Draw Pac-Man using the current sprite and visual position."""
    player = level.player
    sprite = player.sprite_path[player.direction]
    dimensions = (sprite.get_width(), sprite.get_height())

    canvas.blit(
        sprite,
        sprite_position(player.position, dimensions),
    )


def render_collectibles(
    canvas: pg.Surface,
    level: Level,
    sprite_position: SpritePosition,
) -> None:
    """Draw remaining pacgums at their maze positions."""
    for position, pacgum in level.pacgums.items():
        sprite = pacgum[1]
        dimensions = (sprite.get_width(), sprite.get_height())

        canvas.blit(
            sprite,
            sprite_position(position, dimensions),
        )


def render_game(
    canvas: pg.Surface,
    level: Level,
    game_state: GameState | None,
    cheat_mode: CheatMode,
    wall_sprite: pg.Surface,
    maze_layout: list[list[str]],
    block_positions: BlockPositions,
    sprite_position: SpritePosition,
    sprite_animator: SpriteAnimator,
    hud: GameHUD,
    disco_effects: DiscoEffects,
    level_bg: pg.Surface
) -> None:
    """Render the complete active game in its original drawing order."""
    # Clear previous-frame pixels before drawing the current scene.
    canvas.fill((0, 0, 0))
    bg_pos = (
        center(canvas.get_width(), level_bg.get_width()),
        center(canvas.get_height(), level_bg.get_height())
    )
    canvas.blit(level_bg, bg_pos)

    render_maze_walls(
        canvas,
        wall_sprite,
        maze_layout,
        block_positions,
    )

    # Lighting stays behind characters and collectibles.
    if cheat_mode.disco_enabled and block_positions:
        render_disco_effects(
            canvas,
            block_positions,
            wall_sprite,
            disco_effects,
        )

    render_player(canvas, level, sprite_position)

    sprite_animator.render_ghosts(canvas, level)

    if game_state is not None:
        hud.render(
            canvas,
            score=game_state.score,
            level=game_state.current_level,
            lives=game_state.lives,
            remaining_time=level.remaining_time,
            cheats_used=cheat_mode.cheats_used,
        )

    # Draw collectibles last to preserve their visibility.
    render_collectibles(canvas, level, sprite_position)
