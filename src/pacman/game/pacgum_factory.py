"""Create the initial pacgum placement for an active Pac-Man level."""

from random import Random

from src.pacman.game.pacgum import PacgumType
from src.pacman.maze.maze import Maze


def pacgum_factory(
    maze: Maze,
    seed: int,
    pacgum_count: int,
    spawn_position: tuple[int, int],
) -> dict[tuple[int, int], PacgumType]:
    """Create the initial pacgum placement for one level."""

    # Collect positions that are allowed to contain normal pacgums.
    eligible_positions: list[tuple[int, int]] = []

    # Reserve the four maze corners for super-pacgums.
    super_pacgum_positions = frozenset({
        (0, 0),
        (maze.width - 1, 0),
        (0, maze.height - 1),
        (maze.width - 1, maze.height - 1),
    })

    # Visit every maze position and keep only valid normal-pacgum locations.
    for y in range(maze.height):
        for x in range(maze.width):
            position = (x, y)

            # Generator-reserved cells are not playable corridor positions.
            if position in maze.reserved_positions:
                continue

            # Avoid placing a pacgum underneath the player's starting position.
            if position == spawn_position:
                continue

            # Corner positions belong exclusively to super-pacgums.
            if position in super_pacgum_positions:
                continue

            eligible_positions.append(position)

    # Shuffle reproducibly so the same level seed gives the same placement.
    rng = Random(seed)
    rng.shuffle(eligible_positions)

    # Select the requested number, or all available positions if fewer exist.
    pacgum_positions = eligible_positions[:pacgum_count]

    # Map each selected position to a normal pacgum.
    pacgums = {
        position: PacgumType.PACGUM
        for position in pacgum_positions
    }

    # Add one super-pacgum at each of the four reserved corner positions.
    for position in super_pacgum_positions:
        pacgums[position] = PacgumType.SUPER_PACGUM

    return pacgums
