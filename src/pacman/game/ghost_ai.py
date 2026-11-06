"""Calculate maze distances and choose ghost movement directions."""

from collections import deque

from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.game.ghost import Ghost, GhostState


def calculate_distances(
    maze: Maze,
    start_position: tuple[int, int],
) -> dict[tuple[int, int], int]:
    """Calculate shortest-path distances from a starting maze position."""

    # Track shortest distances, starting at zero.
    distances: dict[tuple[int, int], int] = {start_position: 0}

    # Process nearby cells first using a FIFO queue.
    queue = deque([start_position])

    # Explore reachable cells in order of increasing distance.
    while queue:
        current_position = queue.popleft()

        for direction in Direction:
            if not maze.can_move(current_position, direction):
                continue

            dx, dy = direction.value
            x, y = current_position
            neighbour = (x + dx, y + dy)

            # Skip cells already discovered through a shortest route.
            if neighbour in distances:
                continue

            distances[neighbour] = distances[current_position] + 1
            queue.append(neighbour)

    return distances


def choose_ghost_direction(
    ghost: Ghost,
    maze: Maze,
    distances: dict[tuple[int, int], int],
) -> Direction | None:
    """Choose a legal direction based on the ghost's behaviour state."""

    # Remember the best reachable move found so far.
    best_direction: Direction | None = None
    best_distance: int | None = None

    # Compare legal neighbours using their shortest-path distances.
    for direction in Direction:
        if not maze.can_move(ghost.position, direction):
            continue

        dx, dy = direction.value
        x, y = ghost.position
        neighbour = (x + dx, y + dy)

        if neighbour not in distances:
            continue

        distance = distances[neighbour]

        if (
            best_distance is None
            or (
                ghost.state == GhostState.ENRAGED
                and distance < best_distance
            )
            or (
                ghost.state == GhostState.FRIGHTENED
                and distance > best_distance
            )
        ):
            best_direction = direction
            best_distance = distance

    return best_direction
