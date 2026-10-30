"""Represent an active Pac-Man level and its level-specific state."""

from src.pacman.config.models import LevelConfig
from src.pacman.maze.maze import Maze
from src.pacman.game.pacgum import PacgumType
from src.pacman.game.player import Player


class Level:
    """Represent one active level and its mutable level specific state."""

    def __init__(
        self,
        config: LevelConfig,
        maze: Maze,
        player: Player,
        time_limit: int,
        pacgums: dict[tuple[int, int], PacgumType],
    ) -> None:
        """Receive the initial pieces for one level, and create level state."""

        self.config = config
        self.maze = maze
        self.remaining_time = time_limit
        self.player = player
        self.pacgums = pacgums

    def collect_pacgum(
        self,
        position: tuple[int, int],
    ) -> PacgumType | None:
        """Remove and return the pacgum at a position, if present."""

        return self.pacgums.pop(position, None)

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

    @property
    def is_complete(
        self,
    ) -> bool:
        """Return whether the level is complete."""

        return not self.pacgums
