
"""Create reachable pacgum placement for an active Pac-Man level."""

from random import Random

from pacman.game.pacgum import PacgumType
from pacman.maze.maze import Maze
from pacman.app.actions import IMAGES, load_trans_image
import pygame as pg


def pacgum_factory(
    maze: Maze,
    seed: int,
    pacgum_count: int,
    spawn_position: tuple[int, int],
    reachable_positions: set[tuple[int, int]],
) -> dict[tuple[int, int], tuple[PacgumType, pg.Surface]]:
    """Place four corner super-pacgums and reachable normal pacgums."""

    if pacgum_count < 0:
        raise ValueError("Pacgum count cannot be negative")

    # Only reachable, nonreserved cells may contain pacgums.
    available_positions = {
        position
        for position in reachable_positions
        if maze.within_bounds(position)
        and position not in maze.reserved_positions
        and position != spawn_position
    }

    required_positions = pacgum_count + 4

    if len(available_positions) < required_positions:
        raise ValueError(
            "Not enough reachable cells for the requested pacgums"
        )

    corner_positions = [
        (0, 0),
        (maze.width - 1, 0),
        (0, maze.height - 1),
        (maze.width - 1, maze.height - 1),
    ]

    pacgums: dict[tuple[int, int], tuple[PacgumType, pg.Surface]] = {}
    dflt_loc: str = f'{IMAGES}/pacgums'
    pacgum_sprite: pg.Surface = load_trans_image(f'{dflt_loc}/pacgum.png')
    super_pacgums: dict[str, pg.Surface] = {
        'wig': load_trans_image(f'{dflt_loc}/wig.png'),
        'fan': load_trans_image(f'{dflt_loc}/fan.png'),
        'dress': load_trans_image(f'{dflt_loc}/dress.png'),
        'heels': load_trans_image(f'{dflt_loc}/heels.png')
    }

    # Assign four distinct, reachable corner-region positions.
    for corner, sprite in zip(corner_positions, super_pacgums):
        position = min(
            available_positions,
            key=lambda candidate: (
                abs(candidate[0] - corner[0])
                + abs(candidate[1] - corner[1]),
                candidate[1],
                candidate[0],
            ),
        )

        pacgums[position] = (PacgumType.SUPER_PACGUM, super_pacgums[sprite])
        available_positions.remove(position)

    # Deterministic placement of the requested normal pacgums.
    eligible_positions = sorted(available_positions)

    rng = Random(seed)
    rng.shuffle(eligible_positions)

    for position in eligible_positions[:pacgum_count]:
        pacgums[position] = (PacgumType.PACGUM, pacgum_sprite)

    return pacgums
