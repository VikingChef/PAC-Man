"""Represent Pac-Man's player state and movement behaviour."""

from src.pacman.maze.direction import Direction
from src.pacman.maze.maze import Maze


class Player:
    """Represent Pac-Man's position, facing direction, and movement state."""

    def __init__(
        self,
        spawn_position: tuple[int, int],
        spawn_direction: Direction,
    ) -> None:
        """Initialize spawn state and current player state."""

        # Keep permanent spawn state separate from mutable current state.
        self.spawn_position = spawn_position
        self.spawn_direction = spawn_direction
        self.position = spawn_position
        self.direction = spawn_direction

    def reset(self) -> None:
        """Reset the player to its spawn position and direction."""

        # Restore the player's live state from its stored spawn state.
        self.position = self.spawn_position
        self.direction = self.spawn_direction

    def move(
        self,
        maze: Maze,
        direction: Direction,
    ) -> bool:
        """Move in the requested direction when the maze allows it."""

        # Stop immediately when the maze blocks the requested movement.
        if not maze.can_move(self.position, direction):
            return False

        # Combine the current position with the direction's movement delta.
        dx, dy = direction.value
        x, y = self.position
        self.position = (
            x + dx,
            y + dy,
        )

        # Keep facing direction aligned with the successful move.
        self.direction = direction

        return True
