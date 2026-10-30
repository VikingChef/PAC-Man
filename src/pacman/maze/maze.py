"""Represent an internal Pac-Man maze and its movement rules."""

from src.pacman.maze.direction import Direction
from src.pacman.maze.wall import Wall


DIRECTION_TO_WALL = {
    Direction.NORTH: Wall.NORTH,
    Direction.SOUTH: Wall.SOUTH,
    Direction.EAST: Wall.EAST,
    Direction.WEST: Wall.WEST,
}


class Maze:
    """Represent maze geometry independently from the external generator."""

    def __init__(
        self,
        maze_grid: list[list[Wall]],
        reserved_positions: frozenset[tuple[int, int]] = frozenset(),
    ) -> None:
        """Initialize maze geometry and generator-reserved positions."""

        self.maze_grid = maze_grid
        self.reserved_positions = reserved_positions

    @property
    def height(self) -> int:
        """Return the number of rows in the maze."""

        return len(self.maze_grid)

    @property
    def width(self) -> int:
        """Return the number of columns in the maze."""

        if not self.maze_grid:
            return 0

        return len(self.maze_grid[0])

    def within_bounds(
        self,
        position: tuple[int, int],
    ) -> bool:
        """Return whether a position lies inside the maze."""

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
        """Return whether movement is possible in the given direction."""

        dx, dy = direction.value
        x, y = position
        destination = (
            x + dx,
            y + dy,
        )

        # Movement cannot leave the maze boundaries.
        if not self.within_bounds(destination):
            return False

        # Movement cannot cross a wall from the current maze cell.
        wall = DIRECTION_TO_WALL[direction]

        return not self.maze_grid[y][x] & wall
