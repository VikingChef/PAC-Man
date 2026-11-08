
"""Represent Pac-Man ghost identity, state, and physical gameplay data."""

from enum import Enum, auto

from pacman.maze.direction import Direction
from pacman.maze.maze import Maze


RESPAWN_DELAY = 5


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
    EATEN = auto()


class Ghost:
    """Represent one active ghost and its lifecycle."""

    def __init__(
        self,
        spawn_position: tuple[int, int],
        identity: GhostIdentity,
        spawn_direction: Direction,
    ) -> None:
        """Initialize ghost identity, spawn data, and current state."""

        self.identity = identity
        self.spawn_position = spawn_position
        self.spawn_direction = spawn_direction

        self.position = spawn_position
        self.direction = spawn_direction
        self.state = GhostState.ENRAGED
        self.respawn_timer = 0

    def reset(self) -> None:
        """Restore the ghost to its initial spawn state."""

        self.position = self.spawn_position
        self.direction = self.spawn_direction
        self.state = GhostState.ENRAGED
        self.respawn_timer = 0

    def eat(self) -> bool:
        """Mark a frightened ghost as eaten and begin its respawn delay."""

        if self.state != GhostState.FRIGHTENED:
            return False

        self.state = GhostState.EATEN
        self.respawn_timer = RESPAWN_DELAY
        return True

    def tick(
        self,
        elapsed_seconds: int,
        frightened_active: bool,
    ) -> None:
        """Count down an eaten ghost's respawn timer."""

        if elapsed_seconds < 0:
            raise ValueError("Elapsed seconds cannot be negative")

        if self.state != GhostState.EATEN:
            return

        self.respawn_timer = max(
            0,
            self.respawn_timer - elapsed_seconds,
        )

        if self.respawn_timer == 0:
            self.reset()

            if frightened_active:
                self.state = GhostState.FRIGHTENED

    def move(
        self,
        maze: Maze,
        direction: Direction,
    ) -> bool:
        """Move one legal cell unless the ghost has been eaten."""

        if self.state == GhostState.EATEN:
            return False

        if not maze.can_move(self.position, direction):
            return False

        dx, dy = direction.value
        x, y = self.position

        self.position = (
            x + dx,
            y + dy,
        )

        self.direction = direction
        return True
