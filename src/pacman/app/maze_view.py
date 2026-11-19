
"""Build the visual maze layout and its canvas coordinates."""

import pygame as pg

from pacman.app.viewport import maze_origin
from pacman.game.level import Level
from pacman.maze.direction import Direction
from pacman.maze.wall import Wall


BlockPosition = tuple[int, int]
BlockPositions = list[list[BlockPosition]]


def interleave_elements(
    source: list,
    separator: str | list,
    size: int,
) -> list:
    """Insert separators between maze elements."""
    result: list = []
    source_index = 0

    for index in range(size * 2):
        if index % 2 == 0:
            result.append(separator)
        else:
            result.append(source[source_index])
            source_index += 1

    result.append(separator)
    return result


def create_visual_paths(
    level: Level,
    layout: list[list[str]],
    width: int,
) -> list[list[str]]:
    """Mark passages using the actual maze movement rules."""
    maze = level.maze

    # Replace separator rows with complete rows of wall blocks.
    for row_index, _ in enumerate(layout):
        if row_index % 2 == 0:
            layout[row_index] = ["wall"] * (width * 2 + 1)

    # Open only passages that the underlying maze permits.
    for row_index, row in enumerate(layout):
        for column_index, cell in enumerate(row):
            if type(cell) is not Wall:
                continue

            position = (
                (column_index - 1) // 2,
                (row_index - 1) // 2,
            )

            if position in maze.reserved_positions:
                layout[row_index][column_index] = "wall"
                continue

            layout[row_index][column_index] = "path"

            if maze.can_move(position, Direction.EAST):
                layout[row_index][column_index + 1] = "path"

            if maze.can_move(position, Direction.SOUTH):
                layout[row_index + 1][column_index] = "path"

    return layout


def build_maze_layout(level: Level) -> list[list[str]]:
    """Transform a logical maze into its visual block layout."""
    width = level.maze.width
    height = level.maze.height

    # Insert visual columns between logical maze cells.
    expanded_rows = [
        interleave_elements(list(row), "wall", width)
        for row in level.maze.maze_grid
    ]

    # Insert visual rows above and below the expanded cells.
    layout = interleave_elements(
        expanded_rows,
        ["wall"],
        height,
    )

    return create_visual_paths(level, layout, width)


def calculate_block_positions(
    layout: list[list[str]],
    wall_sprite: pg.Surface,
) -> BlockPositions:
    """Position visual maze blocks beneath the gameplay HUD."""
    positions: BlockPositions = []

    if not layout:
        return positions

    block_width = wall_sprite.get_width()
    block_height = wall_sprite.get_height()

    maze_width = len(layout[0]) * block_width
    maze_height = len(layout) * block_height

    # Use the existing viewport positioning calculation.
    origin_x, origin_y = maze_origin(
        (maze_width, maze_height)
    )

    for row_index, row in enumerate(layout):
        positions.append([])

        for column_index, _ in enumerate(row):
            x = origin_x + column_index * block_width
            y = origin_y + row_index * block_height
            positions[row_index].append((x, y))

    return positions
