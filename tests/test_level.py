"""Tests for active Pac-Man level state and timer behaviour."""

from pacman.config.models import LevelConfig
from pacman.game.level import Level
from pacman.game.pacgum import PacgumType
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

    # Create the level with a known starting timer and empty pacgum state.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
        pacgums={},
    )

    # Verify that constructor input became the level's initial state.
    assert level.config == config
    assert level.maze == maze
    assert level.player == player
    assert level.remaining_time == 90
    assert level.pacgums == {}


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
        pacgums={},
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
        pacgums={},
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
        pacgums={},
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
        pacgums={},
    )

    # Reduce the timer to half its starting value.
    level.tick(45)

    # The property should report that time remains.
    assert level.is_time_up is False


def test_collect_pacgum_removes_and_returns_pacgum() -> None:
    """Verify that collecting a pacgum removes and returns it."""

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

    # Start the level with one known normal pacgum.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
        pacgums={
            (0, 0): PacgumType.PACGUM,
        },
    )

    # Collect the pacgum from its known position.
    collected = level.collect_pacgum((0, 0))

    # Collection should report the type of pacgum that was removed.
    assert collected == PacgumType.PACGUM

    # The collected pacgum should no longer remain in the level state.
    assert (0, 0) not in level.pacgums


def test_collect_pacgum_returns_none_when_empty() -> None:
    """Verify that collecting from an empty position returns None."""

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

    # Start with no pacgums so the requested position is empty.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
        pacgums={},
    )

    # Attempt to collect from a position containing no pacgum.
    collected = level.collect_pacgum((0, 0))

    # Empty positions should be handled normally rather than raising an error.
    assert collected is None


def test_level_is_not_complete_with_pacgums() -> None:
    """Verify that a level with pacgums remaining is not complete."""

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

    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
        pacgums={
            (0, 0): PacgumType.PACGUM,
        },
    )

    assert level.is_complete is False


def test_level_is_complete_without_pacgums() -> None:
    """Verify that a level without pacgums is complete."""

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

    level = Level(
        config=config,
        maze=maze,
        player=player,
        time_limit=90,
        pacgums={},
    )

    assert level.is_complete is True
