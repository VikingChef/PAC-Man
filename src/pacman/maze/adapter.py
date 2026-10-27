"""Adapt the external A-Maze-ing representation into our internal Maze."""

from mazegenerator.mazegenerator import MazeGenerator

from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


WALL_BIT_MAP = {
    1: Wall.NORTH,
    2: Wall.EAST,
    4: Wall.SOUTH,
    8: Wall.WEST,
}

RESERVED_CELL_VALUE = 15


def convert_maze_grid(
    raw_maze: list[list[int]],
) -> list[list[Wall]]:
    """Convert the external wall bitmasks into internal Wall values."""

    maze_grid: list[list[Wall]] = []

    for raw_row in raw_maze:
        maze_row: list[Wall] = []

        for raw_cell in raw_row:
            walls = Wall.NONE

            # Convert each external wall bit into our internal representation.
            for bit, wall in WALL_BIT_MAP.items():
                if raw_cell & bit:
                    walls |= wall

            maze_row.append(walls)

        maze_grid.append(maze_row)

    return maze_grid


def find_reserved_positions(
    raw_maze: list[list[int]],
) -> frozenset[tuple[int, int]]:
    """Return positions marked as reserved by the external generator."""

    reserved_positions = {
        (x, y)
        for y, row in enumerate(raw_maze)
        for x, cell in enumerate(row)
        if cell == RESERVED_CELL_VALUE
    }

    return frozenset(reserved_positions)


def adapt_maze(generator: MazeGenerator) -> Maze:
    """Convert an external generated maze into our internal Maze."""

    raw_maze = generator.maze

    # Convert generator-specific wall values at the external boundary.
    maze_grid = convert_maze_grid(raw_maze)

    # Preserve generator-reserved cells without leaking their raw encoding.
    reserved_positions = find_reserved_positions(raw_maze)

    return Maze(
        maze_grid=maze_grid,
        reserved_positions=reserved_positions,
    )
