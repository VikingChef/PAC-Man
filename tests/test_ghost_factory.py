"""Tests for ghost creation and spawn placement."""

from pacman.game.ghost import GhostIdentity
from pacman.game.ghost_factory import create_ghosts
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


def test_create_ghosts_uses_expected_spawn_positions() -> None:
    """Verify that four ghosts spawn in the expected maze corners."""

    # Build a realistic 21x21 open maze for spawn-placement testing.
    maze_grid = [
        [Wall.NONE for _ in range(21)]
        for _ in range(21)
    ]

    maze = Maze(maze_grid)

    # Create the four ghosts using the factory under test.
    ghosts = create_ghosts(maze)

    # The factory should always create exactly four ghosts.
    assert len(ghosts) == 4

    # Top-left ghost should use its fixed identity and face inward.
    assert ghosts[0].identity == GhostIdentity.CLOSET_HYPOCRITE
    assert ghosts[0].position == (1, 1)
    assert ghosts[0].direction == Direction.EAST

    # Top-right ghost should use its fixed identity and face inward.
    assert ghosts[1].identity == GhostIdentity.ORANGE_PUNCHLINE
    assert ghosts[1].position == (maze.width - 2, 1)
    assert ghosts[1].direction == Direction.WEST

    # Bottom-left ghost should use its fixed identity and face inward.
    assert ghosts[2].identity == GhostIdentity.EGO_MACHINE
    assert ghosts[2].position == (1, maze.height - 2)
    assert ghosts[2].direction == Direction.EAST

    # Bottom-right ghost should use its fixed identity and face inward.
    assert ghosts[3].identity == GhostIdentity.TERF_HAG
    assert ghosts[3].position == (
        maze.width - 2,
        maze.height - 2,
    )
    assert ghosts[3].direction == Direction.WEST
