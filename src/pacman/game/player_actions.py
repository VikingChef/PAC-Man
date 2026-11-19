
"""Handle player movement and pacgum collection."""

from dataclasses import dataclass

from pacman.game.level import Level
from pacman.game.pacgum import PacgumType
from pacman.maze.direction import Direction


CellPosition = tuple[int, int]


@dataclass(frozen=True)
class PlayerMoveResult:
    """Describe the outcome of a player movement attempt."""

    moved: bool
    previous_position: CellPosition | None = None
    collected_pacgum: PacgumType | None = None
    level_complete: bool = False


def move_and_collect(
    level: Level,
    direction: Direction,
) -> PlayerMoveResult:
    """Move the player and resolve any pacgum collection."""
    previous_position = level.player.position

    moved = level.player.move(level.maze, direction)

    if not moved:
        return PlayerMoveResult(moved=False)

    collected_pacgum = level.collect_pacgum(
        level.player.position
    )

    if collected_pacgum == PacgumType.SUPER_PACGUM:
        level.frighten_ghosts()

    return PlayerMoveResult(
        moved=True,
        previous_position=previous_position,
        collected_pacgum=collected_pacgum,
        level_complete=level.is_complete,
    )
