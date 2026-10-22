"""Process the A-Maze-ing maze into our internal Maze/Wall representation."""

from mazegenerator.mazegenerator import MazeGenerator

from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


# Translate A-Maze-ing wall encoding into readable Wall flags.
WALL_BIT_MAP = {
    1: Wall.NORTH,
    2: Wall.EAST,
    4: Wall.SOUTH,
    8: Wall.WEST,
}


def adapt_maze(
    generator: MazeGenerator,
) -> Maze:
    """Take an external MazeGenerator object and return our internal Maze."""

    # Read the raw wall-encoded maze produced by A-Maze-ing.
    raw_maze = generator.maze
    maze_grid: list[list[Wall]] = []

    # Convert each external maze row into our internal Wall representation.
    for raw_row in raw_maze:
        row: list[Wall] = []

        # Convert each raw cell into a combination of our Wall flags.
        for raw_cell in raw_row:
            walls = Wall.NONE

            # Check which external wall bits are present in this cell.
            for bit, wall in WALL_BIT_MAP.items():
                if raw_cell & bit:
                    walls |= wall

            row.append(walls)

        maze_grid.append(row)

    # Return our Maze so the rest of the game never sees raw A-Maze-ing data.
    return Maze(maze_grid)
