"""Tests for active Pac-Man level state and timer behaviour."""

from pacman.config.models import LevelConfig
from pacman.game.level import Level
from pacman.game.player import Player
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall


def test_level_initializes_state() -> None:
    """Verify that Level stores and initializes relevant data."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Create the level with a known starting timer.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
    )

    # Verify that constructor input became the level's initial state.
    assert level.config == config
    assert level.maze == maze
    assert level.player == player
    assert level.remaining_time == 90


def test_level_tick_reduces_remaining_time() -> None:
    """Verify that tick reduces the remaining level time."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start with a known amount of remaining time.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
    )

    # Simulate ten elapsed seconds.
    level.tick(10)

    # The timer should decrease by exactly the elapsed amount.
    assert level.remaining_time == 80


def test_level_tick_does_not_go_below_zero() -> None:
    """Verify that tick does not go under zero."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start with a known amount of remaining time.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
    )

    # Simulate more elapsed time than remains on the level timer.
    level.tick(100)

    # The timer should clamp at zero instead of becoming negative.
    assert level.remaining_time == 0


def test_time_is_up() -> None:
    """Verify that the level reports when time is up."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start with a known amount of remaining time.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
    )

    # Reduce the timer exactly to zero.
    level.tick(90)

    # The property should report that time is up.
    assert level.is_time_up is True


def test_time_is_left() -> None:
    """Verify that the level reports time is not up before zero."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start with a known amount of remaining time.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
    )

    # Reduce the timer to half its starting value.
    level.tick(45)

    # The property should report that time remains.
    assert level.is_time_up is False
