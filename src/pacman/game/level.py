"""Represent an active Pac-Man level and its level-specific state."""

from pacman.config.models import LevelConfig
from pacman.game.pacgum import PacgumType
from pacman.game.player import Player
from pacman.game.ghost import Ghost, GhostState
from pacman.maze.maze import Maze
from pacman.game.ghost_ai import (
    calculate_distances,
    choose_ghost_direction,
)


class Level:
    """Represent one active level and its mutable level specific state."""

    def __init__(
        self,
        config: LevelConfig,
        maze: Maze,
        player: Player,
        ghosts: list[Ghost],
        time_limit: int,
        pacgums: dict[tuple[int, int], PacgumType],
    ) -> None:
        """Receive the initial pieces for one level, and create level state."""

        self.config = config
        self.maze = maze
        self.remaining_time = time_limit
        self.player = player
        self.ghosts = ghosts
        self.pacgums = pacgums
        # Ghosts begin enraged, so no frightened time is active.
        self.frightened_timer = 0

    def collect_pacgum(
        self,
        position: tuple[int, int],
    ) -> PacgumType | None:
        """Remove and return the pacgum at a position, if present."""

        return self.pacgums.pop(position, None)

    def frighten_ghosts(self) -> None:
        """Set all ghosts to frightened and restart the frightened timer."""

        self.frightened_timer = 6

        for ghost in self.ghosts:
            ghost.state = GhostState.FRIGHTENED

    def move_ghosts(self) -> None:
        """Move each ghost one cell according to its AI behaviour."""

        # Calculate the shortest routes from Pac-Man's position.
        distances = calculate_distances(
            self.maze,
            self.player.position,
        )

        # Choose and perform one movement for each ghost.
        for ghost in self.ghosts:
            direction = choose_ghost_direction(
                ghost,
                self.maze,
                distances,
            )

            if direction is not None:
                ghost.move(self.maze, direction)

    def check_ghost_collision(self) -> list[Ghost]:
        """Return all ghosts occupying the player's position."""

        # Collect every ghost sharing the player's position.
        colliding_ghosts: list[Ghost] = []

        for ghost in self.ghosts:
            if ghost.position == self.player.position:
                colliding_ghosts.append(ghost)

        return colliding_ghosts

    def reset_positions(self) -> None:
        """Return the player and all ghosts to their spawn positions."""

        self.player.reset()

        for ghost in self.ghosts:
            ghost.reset()

        self.frightened_timer = 0

    def tick(
        self,
        elapsed_seconds: int,
    ) -> None:
        """Reduce the level and frightened timers by elapsed seconds."""

        self.remaining_time = max(
            0,
            self.remaining_time - elapsed_seconds,
        )

        # Remember whether the frightened timer was running.
        was_frightened = self.frightened_timer > 0

        self.frightened_timer = max(
            0,
            self.frightened_timer - elapsed_seconds,
        )

        # Restore normal ghost behaviour when frightened time expires.
        if was_frightened and self.frightened_timer == 0:
            for ghost in self.ghosts:
                ghost.state = GhostState.ENRAGED

    @property
    def is_time_up(self) -> bool:
        """Return whether remaining_time has reached zero."""

        return self.remaining_time == 0

    @property
    def is_complete(
        self,
    ) -> bool:
        """Return whether the level is complete."""

        return not self.pacgums
