
"""Tests for Pac-Man ghost pathfinding and direction selection."""

from pacman.game.ghost import Ghost, GhostIdentity, GhostState
from pacman.game.ghost_ai import calculate_distances, choose_ghost_direction
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


def test_calculate_distances_open_maze() -> None:
    """Verify BFS calculates shortest distances in an open maze."""

    maze = Maze([
        [Wall.NONE, Wall.NONE, Wall.NONE],
        [Wall.NONE, Wall.NONE, Wall.NONE],
        [Wall.NONE, Wall.NONE, Wall.NONE],
    ])

    distances = calculate_distances(maze, (0, 0))

    assert distances[(0, 0)] == 0
    assert distances[(1, 0)] == 1
    assert distances[(0, 1)] == 1
    assert distances[(2, 2)] == 4
    assert len(distances) == 9


def test_calculate_distances_around_wall() -> None:
    """Verify BFS finds a route around a blocked passage."""

    # Block the direct middle passage in both directions.
    maze = Maze([
        [Wall.NONE, Wall.NONE, Wall.NONE],
        [Wall.EAST, Wall.WEST, Wall.NONE],
        [Wall.NONE, Wall.NONE, Wall.NONE],
    ])

    distances = calculate_distances(maze, (2, 1))

    # The direct route is blocked, requiring a four-step detour.
    assert distances[(0, 1)] == 4
    assert distances[(2, 1)] == 0


def test_calculate_distances_unreachable_cell() -> None:
    """Verify unreachable cells are excluded from the distance map."""

    maze = Maze([
        [Wall.EAST, Wall.WEST],
    ])

    distances = calculate_distances(maze, (0, 0))

    assert distances == {(0, 0): 0}


def test_enraged_ghost_chases_player() -> None:
    """Verify an enraged ghost chooses the shortest route to Pac-Man."""

    maze = Maze([
        [Wall.NONE, Wall.NONE, Wall.NONE, Wall.NONE],
    ])

    ghost = Ghost(
        spawn_position=(1, 0),
        identity=GhostIdentity.CLOSET_HYPOCRITE,
        spawn_direction=Direction.EAST,
    )

    distances = calculate_distances(maze, (3, 0))
    direction = choose_ghost_direction(ghost, maze, distances)

    assert direction == Direction.EAST


def test_frightened_ghost_flees_player() -> None:
    """Verify a frightened ghost prefers moving away from Pac-Man."""

    maze = Maze([
        [Wall.NONE, Wall.NONE, Wall.NONE, Wall.NONE],
    ])

    ghost = Ghost(
        spawn_position=(1, 0),
        identity=GhostIdentity.CLOSET_HYPOCRITE,
        spawn_direction=Direction.EAST,
    )
    ghost.state = GhostState.FRIGHTENED

    distances = calculate_distances(maze, (3, 0))
    direction = choose_ghost_direction(ghost, maze, distances)

    assert direction == Direction.WEST


def test_enraged_ghost_navigates_around_wall() -> None:
    """Verify chasing follows a legal detour around blocked movement."""

    # East and south are blocked, leaving north as the escape route.
    maze = Maze([
        [Wall.NONE, Wall.NONE, Wall.NONE],
        [Wall.EAST | Wall.SOUTH, Wall.WEST, Wall.NONE],
        [Wall.NORTH, Wall.NONE, Wall.NONE],
    ])

    ghost = Ghost(
        spawn_position=(0, 1),
        identity=GhostIdentity.ORANGE_PUNCHLINE,
        spawn_direction=Direction.EAST,
    )

    distances = calculate_distances(maze, (2, 1))
    direction = choose_ghost_direction(ghost, maze, distances)

    assert direction == Direction.NORTH


def test_ghost_with_no_legal_moves() -> None:
    """Verify a trapped ghost returns no movement direction."""

    maze = Maze([
        [Wall.NONE],
    ])

    ghost = Ghost(
        spawn_position=(0, 0),
        identity=GhostIdentity.EGO_MACHINE,
        spawn_direction=Direction.NORTH,
    )

    distances = calculate_distances(maze, (0, 0))
    direction = choose_ghost_direction(ghost, maze, distances)

    assert direction is None


def test_direction_selection_does_not_move_ghost() -> None:
    """Verify AI chooses directions without changing ghost state."""

    maze = Maze([
        [Wall.NONE, Wall.NONE, Wall.NONE],
    ])

    ghost = Ghost(
        spawn_position=(0, 0),
        identity=GhostIdentity.TERF_HAG,
        spawn_direction=Direction.NORTH,
    )

    distances = calculate_distances(maze, (2, 0))
    direction = choose_ghost_direction(ghost, maze, distances)

    assert direction == Direction.EAST
    assert ghost.position == (0, 0)
    assert ghost.direction == Direction.NORTH
    assert ghost.state == GhostState.ENRAGED
