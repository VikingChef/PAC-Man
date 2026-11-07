"""Represent an internal Pac-Man maze and its movement rules."""

from pacman.maze.direction import Direction
from pacman.maze.wall import Wall


DIRECTION_TO_WALL = {
    Direction.NORTH: Wall.NORTH,
    Direction.SOUTH: Wall.SOUTH,
    Direction.EAST: Wall.EAST,
    Direction.WEST: Wall.WEST,
}

OPPOSITE_WALL = {
    Direction.NORTH: Wall.SOUTH,
    Direction.SOUTH: Wall.NORTH,
    Direction.EAST: Wall.WEST,
    Direction.WEST: Wall.EAST,
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
        """Return whether movement is possible between two maze cells."""

        if not self.within_bounds(position):
            return False

        dx, dy = direction.value
        x, y = position
        destination = (x + dx, y + dy)

        if not self.within_bounds(destination):
            return False

        if position in self.reserved_positions:
            return False

        if destination in self.reserved_positions:
            return False

        current_walls = self.maze_grid[y][x]
        destination_walls = self.maze_grid[destination[1]][destination[0]]

        if current_walls & DIRECTION_TO_WALL[direction]:
            return False

        if destination_walls & OPPOSITE_WALL[direction]:
            return False

        return True
