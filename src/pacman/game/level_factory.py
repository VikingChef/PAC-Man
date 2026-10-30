"""Create active Pac-Man levels from configuration and maze generation."""

from random import Random

from mazegenerator.mazegenerator import MazeGenerator

from pacman.config.models import LevelConfig
from pacman.game.level import Level
from pacman.game.pacgum_factory import pacgum_factory
from pacman.game.player import Player
from pacman.maze.adapter import adapt_maze
from pacman.maze.direction import Direction


def create_level(
    config: LevelConfig,
    seed: int,
    time_limit: int,
    pacgum_count: int,
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

    # Place the player in the middle of the generated maze as required.
    spawn_position = (
        maze.width // 2,
        maze.height // 2,
    )

    # Give the player a reproducible random starting direction.
    rng = Random(seed)
    spawn_direction = rng.choice(list(Direction))
    player = Player(
        spawn_position=spawn_position,
        spawn_direction=spawn_direction,
    )

    # Create the initial pacgum state for this level.
    pacgums = pacgum_factory(
        maze=maze,
        seed=seed,
        pacgum_count=pacgum_count,
        spawn_position=spawn_position,
    )

    # Return the complete active level and its initial mutable state.
    return Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=time_limit,
        pacgums=pacgums,
    )
