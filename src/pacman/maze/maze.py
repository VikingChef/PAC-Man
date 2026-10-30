"""Represent the maze and determine valid positions and movement."""

from src.pacman.maze.direction import Direction
from src.pacman.maze.wall import Wall

DIRECTION_TO_WALL = {
    Direction.NORTH: Wall.NORTH,
    Direction.SOUTH: Wall.SOUTH,
    Direction.EAST: Wall.EAST,
    Direction.WEST: Wall.WEST,
}


class Maze:
    """Represent the maze structure and provide movement/position checks."""

    def __init__(
        self,
        maze_grid: list[list[Wall]]
    ) -> None:
        """Create a maze from the provided maze grid."""

        self.maze_grid = maze_grid

    @property
    def height(self) -> int:
        """Return the height of the maze."""

        return len(self.maze_grid)

    @property
    def width(self) -> int:
        """Return the width of the maze."""

        return len(self.maze_grid[0])

    def within_bounds(
        self,
        position: tuple[int, int]
    ) -> bool:
        """Return whether a position is within maze boundaries."""

        x, y = position

        return (
            0 <= x < self.width
            and 0 <= y < self.height
        )

    def can_move(
        self,
        position: tuple[int, int],
        direction: Direction,
    ) -> bool:
        """Return whether the proposed movement direction is viable."""

# calculate the destination from the current position and movement direction
        x, y = position
        dx, dy = direction.value
        destination = (x + dx, y + dy)

        if not self.within_bounds(destination):
            return False

        wall = DIRECTION_TO_WALL[direction]

        if self.maze_grid[y][x] & wall:
            return False

        return True
