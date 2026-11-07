"""Represent Pac-Man ghost identity, state, and physical gameplay data."""

from enum import Enum, auto

from pacman.maze.direction import Direction
from pacman.maze.maze import Maze


class GhostIdentity(Enum):
    """Identify each distinct ghost character."""

    CLOSET_HYPOCRITE = auto()
    ORANGE_PUNCHLINE = auto()
    EGO_MACHINE = auto()
    TERF_HAG = auto()


class GhostState(Enum):
    """Represent a ghost's current behaviour state."""

    ENRAGED = auto()
    FRIGHTENED = auto()


class Ghost:
    """Represent one active ghost."""

    def __init__(
        self,
        spawn_position: tuple[int, int],
        identity: GhostIdentity,
        spawn_direction: Direction,
    ) -> None:
        """Initialize ghost identity, spawn state, and current state."""

        self.identity = identity
        self.spawn_position = spawn_position
        self.spawn_direction = spawn_direction

        self.position = spawn_position
        self.direction = spawn_direction
        self.state = GhostState.ENRAGED

    def reset(
        self,
    ) -> None:
        """Reset the ghost to its spawn state."""

        self.position = self.spawn_position
        self.direction = self.spawn_direction
        self.state = GhostState.ENRAGED

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
