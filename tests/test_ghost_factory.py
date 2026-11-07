
"""Tests for creating ghosts at reachable corner positions."""

import pytest

from pacman.game.ghost import GhostIdentity
from pacman.game.ghost_factory import create_ghosts
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


def make_open_maze(width: int, height: int) -> Maze:
    """Create an open maze for testing ghost placement."""
    return Maze(
        maze_grid=[
            [Wall.NONE for _ in range(width)]
            for _ in range(height)
        ],
    )


def test_create_ghosts_uses_preferred_corner_positions() -> None:
    """Keep original corner spawns when they are reachable."""
    maze = make_open_maze(21, 21)

    reachable_positions = {
        (x, y)
        for y in range(maze.height)
        for x in range(maze.width)
    }

    ghosts = create_ghosts(
        maze=maze,
        reachable_positions=reachable_positions,
        player_spawn=(10, 10),
    )

    assert len(ghosts) == 4

    expected_ghosts = [
        (
            GhostIdentity.CLOSET_HYPOCRITE,
            (1, 1),
            Direction.EAST,
        ),
        (
            GhostIdentity.ORANGE_PUNCHLINE,
            (19, 1),
            Direction.WEST,
        ),
        (
            GhostIdentity.EGO_MACHINE,
            (1, 19),
            Direction.EAST,
        ),
        (
            GhostIdentity.TERF_HAG,
            (19, 19),
            Direction.WEST,
        ),
    ]

    for ghost, (identity, position, direction) in zip(
        ghosts, expected_ghosts
    ):
        assert ghost.identity == identity
        assert ghost.spawn_position == position
        assert ghost.spawn_direction == direction
        assert ghost.position == position
        assert ghost.direction == direction


def test_ghosts_fall_back_to_distinct_reachable_positions() -> None:
    """Use distinct reachable alternatives when corner cells are blocked."""
    maze = make_open_maze(7, 7)

    # Deliberately exclude all four preferred ghost positions.
    reachable_positions = {
        (2, 2),
        (3, 2),
        (4, 2),
        (2, 3),
        (3, 3),
        (4, 3),
        (2, 4),
        (3, 4),
        (4, 4),
    }

    player_spawn = (3, 3)

    ghosts = create_ghosts(
        maze=maze,
        reachable_positions=reachable_positions,
        player_spawn=player_spawn,
    )

    positions = [ghost.spawn_position for ghost in ghosts]

    assert len(ghosts) == 4
    assert len(set(positions)) == 4
    assert all(
        position in reachable_positions
        for position in positions
    )
    assert player_spawn not in positions

    # Each ghost should occupy the nearest available corner cell.
    assert positions == [
        (2, 2),
        (4, 2),
        (2, 4),
        (4, 4),
    ]


def test_ghost_placement_is_deterministic() -> None:
    """Identical reachable positions produce identical ghost spawns."""
    maze = make_open_maze(7, 7)

    reachable_positions = {
        (x, y)
        for y in range(1, 6)
        for x in range(1, 6)
    }

    first_ghosts = create_ghosts(
        maze=maze,
        reachable_positions=reachable_positions,
        player_spawn=(3, 3),
    )

    second_ghosts = create_ghosts(
        maze=maze,
        reachable_positions=reachable_positions,
        player_spawn=(3, 3),
    )

    assert [
        ghost.spawn_position for ghost in first_ghosts
    ] == [
        ghost.spawn_position for ghost in second_ghosts
    ]


def test_ghost_factory_rejects_insufficient_spawn_positions() -> None:
    """Fail clearly when four distinct ghost spawns are impossible."""
    maze = make_open_maze(5, 5)

    reachable_positions = {
        (2, 2),
        (1, 2),
        (2, 1),
        (3, 2),
    }

    with pytest.raises(
        ValueError,
        match="Not enough reachable cells for ghost spawns",
    ):
        create_ghosts(
            maze=maze,
            reachable_positions=reachable_positions,
            player_spawn=(2, 2),
        )
