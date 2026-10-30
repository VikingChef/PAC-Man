"""Tests for Pac-Man player state and movement."""

from pacman.game.player import Player
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


def test_player_initializes_spawn_and_current_state() -> None:
    """Verify that Player initializes spawn and current state."""

    # Create a player with a known spawn position and facing direction.
    player = Player(
        spawn_position=(3, 4),
        spawn_direction=Direction.EAST,
    )

    # Spawn state should also initialize the current live state.
    assert player.spawn_position == (3, 4)
    assert player.spawn_direction == Direction.EAST
    assert player.position == (3, 4)
    assert player.direction == Direction.EAST


def test_player_reset_restores_spawn_state() -> None:
    """Verify that reset restores the player's spawn state."""

    # Create the player, then deliberately alter its live state.
    player = Player(
        spawn_position=(3, 4),
        spawn_direction=Direction.EAST,
    )

    player.position = (7, 8)
    player.direction = Direction.NORTH

    # Restore the stored spawn state.
    player.reset()

    # Current state should once again match the spawn state.
    assert player.position == (3, 4)
    assert player.direction == Direction.EAST


def test_player_movement_confirmed() -> None:
    """Verify that player movement returns true."""

    # Create a two-cell maze with an open path to the east.
    maze = Maze([
        [Wall.NONE, Wall.NONE],
    ])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Attempt a legal move into the neighbouring cell.
    moved = player.move(
        maze,
        Direction.EAST,
    )

    # Successful movement should update both position and facing.
    assert moved is True
    assert player.position == (1, 0)
    assert player.direction == Direction.EAST


def test_player_movement_blocked() -> None:
    """Verify that blocked movement leaves player state unchanged."""

    # Block the eastern edge of the player's starting cell.
    maze = Maze([
        [Wall.EAST, Wall.NONE],
    ])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Attempt movement through the blocked edge.
    moved = player.move(
        maze,
        Direction.EAST,
    )

    # Failed movement should leave all live state unchanged.
    assert moved is False
    assert player.position == (0, 0)
    assert player.direction == Direction.EAST
