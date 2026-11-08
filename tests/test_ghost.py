
"""Tests for Pac-Man ghost state, movement, and respawn behaviour."""

from pacman.game.ghost import (
    RESPAWN_DELAY,
    Ghost,
    GhostIdentity,
    GhostState,
)
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


def make_ghost() -> Ghost:
    """Create a ghost with a known initial state."""
    return Ghost(
        spawn_position=(0, 0),
        identity=GhostIdentity.CLOSET_HYPOCRITE,
        spawn_direction=Direction.EAST,
    )


def test_ghost_initializes_state() -> None:
    """Verify identity, position, direction, and initial state."""
    ghost = make_ghost()

    assert ghost.identity == GhostIdentity.CLOSET_HYPOCRITE
    assert ghost.spawn_position == (0, 0)
    assert ghost.spawn_direction == Direction.EAST

    assert ghost.position == (0, 0)
    assert ghost.direction == Direction.EAST
    assert ghost.state == GhostState.ENRAGED
    assert ghost.respawn_timer == 0


def test_ghost_reset_restores_spawn_state() -> None:
    """Verify reset restores the ghost's original state."""
    ghost = make_ghost()

    ghost.position = (1, 1)
    ghost.direction = Direction.WEST
    ghost.state = GhostState.FRIGHTENED

    ghost.reset()

    assert ghost.position == (0, 0)
    assert ghost.direction == Direction.EAST
    assert ghost.state == GhostState.ENRAGED
    assert ghost.respawn_timer == 0


def test_frightened_ghost_can_be_eaten() -> None:
    """Eating a frightened ghost starts its respawn timer."""
    ghost = make_ghost()
    ghost.state = GhostState.FRIGHTENED

    assert ghost.eat() is True
    assert ghost.state == GhostState.EATEN
    assert ghost.respawn_timer == RESPAWN_DELAY


def test_enraged_ghost_cannot_be_eaten() -> None:
    """An enraged ghost must not enter the eaten state."""
    ghost = make_ghost()

    assert ghost.eat() is False
    assert ghost.state == GhostState.ENRAGED
    assert ghost.respawn_timer == 0


def test_eaten_ghost_cannot_be_eaten_twice() -> None:
    """Repeated eating must not restart the respawn countdown."""
    ghost = make_ghost()
    ghost.state = GhostState.FRIGHTENED

    ghost.eat()
    ghost.tick(2, frightened_active=True)

    assert ghost.eat() is False
    assert ghost.respawn_timer == RESPAWN_DELAY - 2


def test_eaten_ghost_cannot_move() -> None:
    """Eaten ghosts remain inactive until they respawn."""
    maze = Maze([
        [Wall.NONE, Wall.NONE],
        [Wall.NONE, Wall.NONE],
    ])

    ghost = make_ghost()
    ghost.state = GhostState.FRIGHTENED
    ghost.eat()

    assert ghost.move(maze, Direction.EAST) is False
    assert ghost.position == (0, 0)


def test_eaten_ghost_counts_down() -> None:
    """The respawn delay decreases with elapsed gameplay time."""
    ghost = make_ghost()
    ghost.state = GhostState.FRIGHTENED
    ghost.eat()

    ghost.tick(2, frightened_active=True)

    assert ghost.state == GhostState.EATEN
    assert ghost.respawn_timer == RESPAWN_DELAY - 2


def test_eaten_ghost_respawns_enraged() -> None:
    """Respawn normally when frightened mode has expired."""
    ghost = make_ghost()
    ghost.position = (3, 4)
    ghost.direction = Direction.NORTH
    ghost.state = GhostState.FRIGHTENED
    ghost.eat()

    ghost.tick(RESPAWN_DELAY, frightened_active=False)

    assert ghost.position == ghost.spawn_position
    assert ghost.direction == ghost.spawn_direction
    assert ghost.state == GhostState.ENRAGED
    assert ghost.respawn_timer == 0


def test_eaten_ghost_respawns_frightened() -> None:
    """Preserve the frightened effect when it remains active."""
    ghost = make_ghost()
    ghost.position = (3, 4)
    ghost.state = GhostState.FRIGHTENED
    ghost.eat()

    ghost.tick(RESPAWN_DELAY, frightened_active=True)

    assert ghost.position == ghost.spawn_position
    assert ghost.state == GhostState.FRIGHTENED
    assert ghost.respawn_timer == 0


def test_reset_cancels_pending_respawn() -> None:
    """Resetting a level must clear any unfinished respawn."""
    ghost = make_ghost()
    ghost.state = GhostState.FRIGHTENED
    ghost.eat()

    ghost.tick(2, frightened_active=True)
    ghost.reset()

    assert ghost.position == ghost.spawn_position
    assert ghost.state == GhostState.ENRAGED
    assert ghost.respawn_timer == 0
