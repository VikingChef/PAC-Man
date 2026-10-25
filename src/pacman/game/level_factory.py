"""Create active Pac-Man levels from configuration and maze generation."""

from mazegenerator.mazegenerator import MazeGenerator

from pacman.config.models import LevelConfig
from pacman.game.level import Level
from pacman.maze.adapter import adapt_maze


def create_level(
    config: LevelConfig,
    seed: int,
    time_limit: int,
) -> Level:
    """Create an active Level from configuration and maze settings."""

    # Generate the external maze using this level's configured dimensions.
    generator = MazeGenerator(
        size=(config.width, config.height),
        perfect=False,
        seed=seed,
    )

    # Cross the adapter boundary into our internal maze representation.
    maze = adapt_maze(generator)

    # Return the active level with its initial mutable state.
    return Level(
        config=config,
        maze=maze,
        time_limit=time_limit,
    )
