"""Create the four ghosts for an active Pac-Man level."""

from pacman.game.ghost import Ghost, GhostIdentity
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze


def create_ghosts(
    maze: Maze,
) -> list[Ghost]:
    """Create the four ghosts for one maze."""

    # Keep all ghost spawns one cell inside the maze border.
    top_left = (1, 1)
    top_right = (maze.width - 2, 1)
    bottom_left = (1, maze.height - 2)
    bottom_right = (maze.width - 2, maze.height - 2)

    # Top-left ghost starts on the left side and faces inward.
    top_left_ghost = Ghost(
        spawn_position=top_left,
        identity=GhostIdentity.CLOSET_HYPOCRITE,
        spawn_direction=Direction.EAST,
    )

    # Top-right ghost starts on the right side and faces inward.
    top_right_ghost = Ghost(
        spawn_position=top_right,
        identity=GhostIdentity.ORANGE_PUNCHLINE,
        spawn_direction=Direction.WEST,
    )

    # Bottom-left ghost starts on the left side and faces inward.
    bottom_left_ghost = Ghost(
        spawn_position=bottom_left,
        identity=GhostIdentity.EGO_MACHINE,
        spawn_direction=Direction.EAST,
    )

    # Bottom-right ghost starts on the right side and faces inward.
    bottom_right_ghost = Ghost(
        spawn_position=bottom_right,
        identity=GhostIdentity.TERF_HAG,
        spawn_direction=Direction.WEST,
    )

    # Return ghosts in a stable order for level setup and testing.
    return [
        top_left_ghost,
        top_right_ghost,
        bottom_left_ghost,
        bottom_right_ghost,
    ]
