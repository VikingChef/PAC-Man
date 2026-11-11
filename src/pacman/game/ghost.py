
"""Represent Pac-Man ghost identity, state, and physical gameplay data."""

from enum import Enum, auto

import pygame as pg

from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.app.actions import load_trans_image, IMAGES


# Seconds an eaten ghost remains inactive at its spawn position.
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
        sprite_path: str | None = None,
    ) -> None:
        """Initialize ghost identity, spawn data, and current state."""

        self.identity = identity
        self.spawn_position = spawn_position
        self.spawn_direction = spawn_direction

        # Every ghost begins at its spawn in the normal enraged state.
        self.position = spawn_position
        self.direction = spawn_direction
        self.state = GhostState.ENRAGED
        self.respawn_timer = 0

        # The game model can be used without artwork in unit tests.
        # Ghosts created by the factory receive a sprite path for rendering.
        self.sprite: dict[Direction, pg.Surface] = {}

        if sprite_path is not None:
            front = load_trans_image(
                f"{IMAGES}/ghosts/{sprite_path}-front.png"
            )
            self.sprite = {
                Direction.NORTH: front,
                Direction.SOUTH: front,
                Direction.WEST: load_trans_image(
                    f"{IMAGES}/ghosts/{sprite_path}-left.png"
                ),
                Direction.EAST: load_trans_image(
                    f"{IMAGES}/ghosts/{sprite_path}-right.png"
                ),
            }

    def reset(self) -> None:
        """Restore the ghost to its initial spawn state."""

        self.position = self.spawn_position
        self.direction = self.spawn_direction
        self.state = GhostState.ENRAGED
        self.respawn_timer = 0

    def eat(self) -> bool:
        """Return an eaten ghost to spawn and begin its respawn delay."""

        # Only frightened ghosts can be eaten.
        if self.state != GhostState.FRIGHTENED:
            return False

        # Immediately return to spawn without calling reset().
        # reset() would clear the delay and reactivate the ghost.
        self.position = self.spawn_position
        self.direction = self.spawn_direction

        # The ghost remains inactive for five seconds at spawn.
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

        # Active ghosts do not need a respawn countdown.
        if self.state != GhostState.EATEN:
            return

        self.respawn_timer = max(
            0,
            self.respawn_timer - elapsed_seconds,
        )

        # Reactivate the ghost when its waiting period finishes.
        if self.respawn_timer == 0:
            self.reset()

            # If the super-pacgum effect is still active, the ghost
            # returns frightened rather than immediately dangerous.
            if frightened_active:
                self.state = GhostState.FRIGHTENED

    def move(
        self,
        maze: Maze,
        direction: Direction,
    ) -> bool:
        """Move one legal cell unless the ghost has been eaten."""

        # Eaten ghosts stay at spawn until their delay expires.
        if self.state == GhostState.EATEN:
            return False

        # Respect the maze's existing movement restrictions.
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
