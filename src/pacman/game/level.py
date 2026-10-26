"""Represent an active Pac-Man level and its level-specific state."""

from pacman.config.models import LevelConfig
from pacman.game.player import Player
from pacman.maze.maze import Maze


class Level:
    """Represent one active level and its mutable level specific state."""

    def __init__(
        self,
        config: LevelConfig,
        maze: Maze,
        player: Player,
        time_limit: int,
    ) -> None:
        """Receive the initial pieces for one level, and create level state."""

        self.config = config
        self.maze = maze
        self.remaining_time = time_limit
        self.player = player

    def tick(
        self,
        elapsed_seconds: int
    ) -> None:
        """Reduce the level timer by the elapsed whole seconds."""

        self.remaining_time = max(
            0,
            self.remaining_time - elapsed_seconds,
        )

    @property
    def is_time_up(self) -> bool:
        """Return whether remaining_time has reached zero."""

        return self.remaining_time == 0
