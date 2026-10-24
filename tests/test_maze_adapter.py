"""Tests for converting A-Maze-ing data into our internal maze format."""

from mazegenerator.mazegenerator import MazeGenerator

from pacman.maze.adapter import adapt_maze, convert_maze_grid
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


def test_convert_maze_grid_converts_single_wall() -> None:
    """Convert a single external wall bit into the matching Wall flag."""

    raw_maze = [[1]]

    maze_grid = convert_maze_grid(raw_maze)

    assert maze_grid == [[Wall.NORTH]]


def test_convert_maze_grid_combines_wall_flags() -> None:
    """Combine multiple external wall bits into one Wall value."""

    # A-Maze-ing value 5 contains NORTH (1) and SOUTH (4).
    raw_maze = [[5]]

    maze_grid = convert_maze_grid(raw_maze)

    assert maze_grid == [[Wall.NORTH | Wall.SOUTH]]


def test_convert_maze_grid_preserves_grid_structure() -> None:
    """Convert multiple rows and cells without changing grid structure."""

    raw_maze = [
        [0, 2],
        [8, 15],
    ]

    maze_grid = convert_maze_grid(raw_maze)

    assert maze_grid == [
        [Wall.NONE, Wall.EAST],
        [
            Wall.WEST,
            Wall.NORTH | Wall.EAST | Wall.SOUTH | Wall.WEST,
        ],
    ]


def test_adapt_maze_returns_internal_maze() -> None:
    """Adapt a real MazeGenerator into our internal Maze representation."""

    generator = MazeGenerator(
        size=(15, 15),
        perfect=False,
        seed=0,
    )

    maze = adapt_maze(generator)

    # Verify the external maze has crossed into our internal representation.
    assert isinstance(maze, Maze)
    assert maze.height == len(generator.maze)
    assert maze.width == len(generator.maze[0])

    # No raw integer wall values should remain inside our Maze.
    assert all(
        isinstance(cell, Wall)
        for row in maze.maze_grid
        for cell in row
    )
