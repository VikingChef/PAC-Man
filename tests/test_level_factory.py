
"""Create active Pac-Man levels from configuration and maze generation."""

import contextlib
import io
from random import Random

from mazegenerator.mazegenerator import MazeGenerator

from pacman.config.models import LevelConfig
from pacman.game.ghost_ai import calculate_distances
from pacman.game.ghost_factory import create_ghosts
from pacman.game.level import Level
from pacman.game.pacgum_factory import pacgum_factory
from pacman.game.player import Player
from pacman.maze.adapter import adapt_maze
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.app.actions import CharSelectAction


def find_player_spawn(
    maze: Maze,
    pacgum_count: int,
) -> tuple[int, int]:
    """Find a central spawn in a sufficiently large reachable region."""

    centre_x = maze.width // 2
    centre_y = maze.height // 2

    # One player position, four super-pacgums, and normal pacgums.
    required_cells = pacgum_count + 5

    candidates: list[tuple[int, int, int]] = []

    for y in range(maze.height):
        for x in range(maze.width):
            position = (x, y)

            if position in maze.reserved_positions:
                continue

            if not any(
                maze.can_move(position, direction)
                for direction in Direction
            ):
                continue

            distance = abs(x - centre_x) + abs(y - centre_y)
            candidates.append((distance, y, x))

    candidates.sort()

    # Prefer the nearest playable centre position, provided its
    # connected region can accommodate the required collectibles.
    for _, y, x in candidates:
        position = (x, y)
        reachable_positions = calculate_distances(maze, position)

        if len(reachable_positions) >= required_cells:
            return position

    raise ValueError(
        "Maze has no connected region large enough for this level"
    )


def create_level(
    config: LevelConfig,
    seed: int,
    time_limit: int,
    pacgum_count: int,
    player_sprite: CharSelectAction | None = None,
) -> Level:
    """Create a playable level from configuration and maze settings."""

    # Generate the maze using the assigned external package.
    with contextlib.redirect_stdout(io.StringIO()):
        generator = MazeGenerator(
            size=(config.width, config.height),
            perfect=False,
            seed=seed,
        )

    maze = adapt_maze(generator)

    # Select the central playable region before placing game objects.
    spawn_position = find_player_spawn(maze, pacgum_count)

    # Share one authoritative reachable region with both factories.
    reachable_positions = set(
        calculate_distances(maze, spawn_position)
    )

    # Place ghosts near their designated corners.
    ghosts = create_ghosts(
        maze=maze,
        reachable_positions=reachable_positions,
        player_spawn=spawn_position,
    )

    # Select the player's starting direction reproducibly.
    rng = Random(seed)
    spawn_direction = rng.choice(list(Direction))

    # Character selection controls artwork, not the player's movement rules.
    # Tests may omit the selection to create a player without loading sprites.
    sprite_path: str | None = None
    if player_sprite == CharSelectAction.MS_POWER_PELLET:
        sprite_path = 'ms-pellet'
    elif player_sprite == CharSelectAction.WAKA_WAKA_WANDA:
        sprite_path = 'waka'

    player = Player(
        spawn_position=spawn_position,
        spawn_direction=spawn_direction,
        path=sprite_path,
    )

    # Place all required pacgums inside the same reachable region.
    pacgums = pacgum_factory(
        maze=maze,
        seed=seed,
        pacgum_count=pacgum_count,
        spawn_position=spawn_position,
        reachable_positions=reachable_positions,
    )

    return Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=time_limit,
        pacgums=pacgums,
    )
