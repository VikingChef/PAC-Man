"""Tests for Pac-Man ghost state and reset behaviour."""

from pacman.game.ghost import Ghost, GhostIdentity, GhostState
from pacman.maze.direction import Direction


def test_ghost_initializes_state() -> None:
    """Verify that Ghost initializes its identity and spawn state."""

    # Create one ghost with known identity, spawn position, and direction.
    ghost = Ghost(
        spawn_position=(0, 0),
        identity=GhostIdentity.CLOSET_HYPOCRITE,
        spawn_direction=Direction.EAST,
    )

    # Fixed identity and spawn data should be stored unchanged.
    assert ghost.identity == GhostIdentity.CLOSET_HYPOCRITE
    assert ghost.spawn_position == (0, 0)
    assert ghost.spawn_direction == Direction.EAST

    # Mutable live state should begin from the stored spawn state.
    assert ghost.position == (0, 0)
    assert ghost.direction == Direction.EAST
    assert ghost.state == GhostState.ENRAGED


def test_ghost_reset_restores_spawn_state() -> None:
    """Verify that reset restores the ghost's spawn state."""

    # Create a ghost with known spawn state.
    ghost = Ghost(
        spawn_position=(0, 0),
        identity=GhostIdentity.CLOSET_HYPOCRITE,
        spawn_direction=Direction.EAST,
    )

    # Change the ghost's mutable live state away from its spawn values.
    ghost.position = (1, 1)
    ghost.direction = Direction.WEST
    ghost.state = GhostState.FRIGHTENED

    # Reset the ghost back to its original spawn state.
    ghost.reset()

    # Position, direction, and behaviour state should all be restored.
    assert ghost.position == (0, 0)
    assert ghost.direction == Direction.EAST
    assert ghost.state == GhostState.ENRAGED
