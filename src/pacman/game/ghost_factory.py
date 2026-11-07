
"""Create the four ghosts for an active Pac-Man level."""

from pacman.game.ghost import Ghost, GhostIdentity
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze


def create_ghosts(
    maze: Maze,
    reachable_positions: set[tuple[int, int]],
    player_spawn: tuple[int, int],
) -> list[Ghost]:
    """Place four ghosts near their corners in reachable maze cells."""

    corner_specs = [
        (
            (1, 1),
            GhostIdentity.CLOSET_HYPOCRITE,
            Direction.EAST,
        ),
        (
            (maze.width - 2, 1),
            GhostIdentity.ORANGE_PUNCHLINE,
            Direction.WEST,
        ),
        (
            (1, maze.height - 2),
            GhostIdentity.EGO_MACHINE,
            Direction.EAST,
        ),
        (
            (maze.width - 2, maze.height - 2),
            GhostIdentity.TERF_HAG,
            Direction.WEST,
        ),
    ]

    available_positions = reachable_positions - {player_spawn}
    ghosts: list[Ghost] = []

    for preferred_position, identity, direction in corner_specs:
        if not available_positions:
            raise ValueError("Not enough reachable cells for ghost spawns")

        preferred_x, preferred_y = preferred_position

        spawn_position = min(
            available_positions,
            key=lambda position: (
                abs(position[0] - preferred_x)
                + abs(position[1] - preferred_y),
                position[1],
                position[0],
            ),
        )

        ghosts.append(
            Ghost(
                spawn_position=spawn_position,
                identity=identity,
                spawn_direction=direction,
            )
        )

        available_positions.remove(spawn_position)

    return ghosts
