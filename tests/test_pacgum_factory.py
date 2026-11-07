"""Tests for reachable pacgum placement generation."""

import pytest

from pacman.game.pacgum import PacgumType
from pacman.game.pacgum_factory import pacgum_factory
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


def make_open_maze(
    width: int,
    height: int,
    reserved_positions: frozenset[tuple[int, int]] = frozenset(),
) -> Maze:
    """Create an open maze with optional reserved positions."""
    return Maze(
        maze_grid=[
            [Wall.NONE for _ in range(width)]
            for _ in range(height)
        ],
        reserved_positions=reserved_positions,
    )


def all_positions(maze: Maze) -> set[tuple[int, int]]:
    """Return every cell in the test maze."""
    return {
        (x, y)
        for y in range(maze.height)
        for x in range(maze.width)
    }


def test_pacgum_factory_creates_requested_counts() -> None:
    """Verify the requested normal count and four super-pacgums."""
    maze = make_open_maze(5, 5)

    pacgums = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
        reachable_positions=all_positions(maze),
    )

    assert sum(
        value == PacgumType.PACGUM
        for value in pacgums.values()
    ) == 3

    assert sum(
        value == PacgumType.SUPER_PACGUM
        for value in pacgums.values()
    ) == 4

    assert len(pacgums) == 7


def test_pacgum_factory_uses_exact_corners_when_reachable() -> None:
    """Use the four literal corners when they are available."""
    maze = make_open_maze(5, 5)

    pacgums = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
        reachable_positions=all_positions(maze),
    )

    expected_corners = {
        (0, 0),
        (4, 0),
        (0, 4),
        (4, 4),
    }

    for corner in expected_corners:
        assert pacgums[corner] == PacgumType.SUPER_PACGUM


def test_pacgum_factory_excludes_spawn_position() -> None:
    """Verify that no pacgum is placed on Pac-Man's spawn."""
    maze = make_open_maze(5, 5)

    pacgums = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
        reachable_positions=all_positions(maze),
    )

    assert (2, 2) not in pacgums


def test_pacgum_factory_excludes_reserved_position() -> None:
    """Verify that reserved cells never receive pacgums."""
    maze = make_open_maze(
        5,
        5,
        reserved_positions=frozenset({(1, 1)}),
    )

    pacgums = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
        reachable_positions=all_positions(maze),
    )

    assert (1, 1) not in pacgums


def test_pacgum_factory_is_deterministic_for_same_seed() -> None:
    """Verify that identical seeds produce identical placements."""
    maze = make_open_maze(
        5,
        5,
        reserved_positions=frozenset({(1, 1)}),
    )

    reachable_positions = all_positions(maze)

    pacgums_a = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
        reachable_positions=reachable_positions,
    )
    pacgums_b = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
        reachable_positions=reachable_positions,
    )

    assert pacgums_a == pacgums_b


def test_super_pacgums_fall_back_to_reachable_corners() -> None:
    """Place four distinct super-pacgums near blocked corners."""
    maze = make_open_maze(7, 7)

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

    pacgums = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=2,
        spawn_position=(3, 3),
        reachable_positions=reachable_positions,
    )

    super_positions = {
        position
        for position, kind in pacgums.items()
        if kind == PacgumType.SUPER_PACGUM
    }

    assert super_positions == {
        (2, 2),
        (4, 2),
        (2, 4),
        (4, 4),
    }

    assert len(pacgums) == 6
    assert set(pacgums).issubset(reachable_positions)
    assert (3, 3) not in pacgums


def test_normal_pacgums_stay_in_reachable_region() -> None:
    """Never place normal pacgums in an unreachable region."""
    maze = make_open_maze(7, 7)

    reachable_positions = {
        (x, y)
        for y in range(2, 5)
        for x in range(2, 5)
    }

    pacgums = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=4,
        spawn_position=(3, 3),
        reachable_positions=reachable_positions,
    )

    assert len(pacgums) == 8
    assert set(pacgums).issubset(reachable_positions)

    assert sum(
        kind == PacgumType.PACGUM
        for kind in pacgums.values()
    ) == 4


def test_pacgum_factory_rejects_insufficient_space() -> None:
    """Do not silently omit required pacgums."""
    maze = make_open_maze(5, 5)

    reachable_positions = {
        (1, 1),
        (2, 1),
        (1, 2),
        (2, 2),
        (3, 2),
    }

    with pytest.raises(
        ValueError,
        match="Not enough reachable cells",
    ):
        pacgum_factory(
            maze=maze,
            seed=42,
            pacgum_count=2,
            spawn_position=(2, 2),
            reachable_positions=reachable_positions,
        )


def test_pacgum_factory_rejects_negative_count() -> None:
    """Reject an invalid negative normal-pacgum count."""
    maze = make_open_maze(5, 5)

    with pytest.raises(
        ValueError,
        match="Pacgum count cannot be negative",
    ):
        pacgum_factory(
            maze=maze,
            seed=42,
            pacgum_count=-1,
            spawn_position=(2, 2),
            reachable_positions=all_positions(maze),
        )
