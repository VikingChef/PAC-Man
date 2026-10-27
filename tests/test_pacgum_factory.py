"""Tests for pacgum placement generation."""

from pacman.game.pacgum import PacgumType
from pacman.game.pacgum_factory import pacgum_factory
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


def test_pacgum_factory_creates_requested_counts() -> None:
    """Verify normal and super-pacgum counts."""

    maze_grid = [
        [Wall.NONE for _ in range(5)]
        for _ in range(5)
    ]

    maze = Maze(maze_grid)

    pacgums = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
    )

    normal_pacgum_count = sum(
        pacgum_type == PacgumType.PACGUM
        for pacgum_type in pacgums.values()
    )

    assert normal_pacgum_count == 3

    super_pacgum_count = sum(
        pacgum_type == PacgumType.SUPER_PACGUM
        for pacgum_type in pacgums.values()
    )

    assert super_pacgum_count == 4


def test_pacgum_factory_excludes_spawn_position() -> None:
    """Verify that no pacgum is placed on the player spawn position."""

    maze_grid = [
        [Wall.NONE for _ in range(5)]
        for _ in range(5)
    ]

    maze = Maze(maze_grid)

    pacgums = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
    )

    assert (2, 2) not in pacgums


def test_pacgum_factory_excludes_reserved_position() -> None:
    """Verify that no pacgum is placed on a reserved maze position."""

    maze_grid = [
        [Wall.NONE for _ in range(5)]
        for _ in range(5)
    ]

    maze = Maze(
        maze_grid,
        reserved_positions=frozenset({(1, 1)}),
    )

    pacgums = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
    )

    assert (1, 1) not in pacgums


def test_pacgum_factory_is_deterministic_for_same_seed() -> None:
    """Verify that identical seeds produce identical pacgum placement."""

    maze_grid = [
        [Wall.NONE for _ in range(5)]
        for _ in range(5)
    ]

    maze = Maze(
        maze_grid,
        reserved_positions=frozenset({(1, 1)}),
    )

    pacgums_a = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
    )

    maze_grid = [
        [Wall.NONE for _ in range(5)]
        for _ in range(5)
    ]

    maze = Maze(
        maze_grid,
        reserved_positions=frozenset({(1, 1)}),
    )

    pacgums_b = pacgum_factory(
        maze=maze,
        seed=42,
        pacgum_count=3,
        spawn_position=(2, 2),
    )

    assert pacgums_a == pacgums_b
