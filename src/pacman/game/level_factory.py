"""Create active Pac-Man levels from configuration and maze generation."""

from random import Random

from mazegenerator.mazegenerator import MazeGenerator

from pacman.config.models import LevelConfig
from pacman.game.level import Level
from pacman.game.player import Player
from pacman.maze.adapter import adapt_maze
from pacman.maze.direction import Direction


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

    # Create the player at the maze entrance with a reproducible random facing.
    random = Random(seed)
    spawn_direction = random.choice(list(Direction))
    player = Player(
        spawn_position=generator.maze_entry,
        spawn_direction=spawn_direction,
    )

    # Return the active level with its initial mutable state.
    return Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=time_limit,
    )
