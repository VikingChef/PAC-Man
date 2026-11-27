"""Own visual movement and sprite interpolation for the maze."""

import time

import pygame as pg

from pacman.app.actions import center
from pacman.game.ghost import Ghost, GhostState
from pacman.game.level import Level


CellPosition = tuple[int, int]
BlockPositions = list[list[CellPosition]]
GhostMoves = dict[Ghost, tuple[CellPosition, float]]


class SpriteAnimator:
    """Track and render player and ghost movements independently of logic."""

    def __init__(self, wall_sprite: pg.Surface) -> None:
        """Set up sprite sizes and empty movement state."""
        self.wall_sprite = wall_sprite
        self.block_positions: BlockPositions = []
        self.player_start: CellPosition | None = None
        self.player_end: CellPosition | None = None
        self.player_started_at = 0.0
        self.player_duration = 0.12
        self.ghost_moves: GhostMoves = {}

    def reset(self, block_positions: BlockPositions | None = None) -> None:
        """Clear visual movements and optionally update the maze geometry."""
        if block_positions is not None:
            self.block_positions = block_positions
        self.stop_player_move()
        self.ghost_moves.clear()

    def start_player_move(
        self,
        previous_position: CellPosition,
        destination: CellPosition,
        started_at: float,
    ) -> None:
        """Begin interpolating the player's latest logical move."""
        self.player_start = previous_position
        self.player_end = destination
        self.player_started_at = started_at

    def stop_player_move(self) -> None:
        """Stop interpolating the player's position."""
        self.player_start = None
        self.player_end = None

    def stop_ghost_move(self, ghost: Ghost) -> None:
        """Stop interpolating one ghost after a collision."""
        self.ghost_moves.pop(ghost, None)

    def _cell_position(self, position: CellPosition) -> CellPosition:
        """Convert a logical maze position into canvas coordinates."""
        x, y = position
        return self.block_positions[y * 2 + 1][x * 2 + 1]

    def _interpolated_position(
        self,
        start: CellPosition,
        destination: CellPosition,
        progress: float,
    ) -> CellPosition:
        """Interpolate visual coordinates without moving game objects."""
        origin_x, origin_y = self._cell_position(start)
        target_x, target_y = self._cell_position(destination)
        return (
            round(origin_x + (target_x - origin_x) * progress),
            round(origin_y + (target_y - origin_y) * progress),
        )

    def position(
        self,
        position: CellPosition,
        dimensions: CellPosition,
    ) -> CellPosition:
        """Center a sprite in a maze cell, interpolating player movement."""
        draw_x, draw_y = self._cell_position(position)

        if self.player_start is not None and self.player_end == position:
            progress = min(
                1.0,
                (time.monotonic() - self.player_started_at)
                / self.player_duration,
            )
            draw_x, draw_y = self._interpolated_position(
                self.player_start,
                position,
                progress,
            )
            if progress >= 1.0:
                self.stop_player_move()

        return (
            draw_x + center(self.wall_sprite.get_width(), dimensions[0]),
            draw_y + center(self.wall_sprite.get_height(), dimensions[1]),
        )

    def render_ghosts(self, canvas: pg.Surface, level: Level) -> None:
        """Draw ghosts with state-based sprites and smooth movement."""
        block_width = self.wall_sprite.get_width()
        block_height = self.wall_sprite.get_height()

        for ghost in level.ghosts:
            # Eaten ghosts teleport rather than sliding to their spawn.
            if ghost.state == GhostState.EATEN:
                self.stop_ghost_move(ghost)

                # Preserve the existing respawn blinking behaviour.
                if int(time.monotonic() * 4) % 2 == 0:
                    continue

            # Eaten ghosts have no separate artwork, so use the normal
            # sprite during the visible part of their blinking cycle.
            sprite_state = (
                GhostState.ENRAGED
                if ghost.state == GhostState.EATEN
                else ghost.state
            )

            # Select artwork using both direction and ghost state.
            sprite = ghost.sprite[ghost.direction][sprite_state]
            dimensions = (sprite.get_width(), sprite.get_height())
            draw_x, draw_y = self._cell_position(ghost.position)
            animation = self.ghost_moves.get(ghost)

            if animation is not None:
                start_position, started_at = animation
                duration = level.config.ghost_move_interval_ms / 1000

                # Interpolation changes only the displayed position.
                # The game model remains responsible for movement.
                progress = min(
                    1.0,
                    (time.monotonic() - started_at)
                    / max(duration, 0.001),
                )
                draw_x, draw_y = self._interpolated_position(
                    start_position,
                    ghost.position,
                    progress,
                )

                # Stop tracking animations after they finish.
                if progress >= 1.0:
                    self.stop_ghost_move(ghost)

            canvas.blit(
                sprite,
                (
                    draw_x + center(block_width, dimensions[0]),
                    draw_y + center(block_height, dimensions[1]),
                ),
            )
