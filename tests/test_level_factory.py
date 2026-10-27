"""Tests for constructing active Pac-Man levels."""

from pacman.config.models import LevelConfig
from pacman.game.level import Level
from pacman.game.level_factory import create_level


def test_create_level_builds_active_level() -> None:
    """Verify that create_level builds a configured active level."""

    # Define the level dimensions the factory should use.
    config = LevelConfig(
        number=1,
        width=15,
        height=15,
    )

    # Build one active level from deterministic generation settings.
    level = create_level(
        config=config,
        seed=42,
        time_limit=90,
        pacgum_count=42,
    )

    # Verify that factory input became the expected active level state.
    assert isinstance(level, Level)
    assert level.config == config
    assert level.remaining_time == 90
    assert level.maze.width == 15
    assert level.maze.height == 15

    # The player should begin in the middle of the generated maze.
    assert level.player.spawn_position == (7, 7)
    assert level.player.position == (7, 7)


def test_create_level_is_deterministic_for_same_seed() -> None:
    """Verify that the same seed produces the same maze and pacgum layout."""

    # Use one shared configuration so only generation determinism is tested.
    config = LevelConfig(
        number=1,
        width=15,
        height=15,
    )

    # Generate two levels from identical inputs.
    level_a = create_level(
        config=config,
        seed=42,
        time_limit=90,
        pacgum_count=42,
    )

    level_b = create_level(
        config=config,
        seed=42,
        time_limit=90,
        pacgum_count=42,
    )

    # Matching seeds should produce identical generated level state.
    assert level_a.maze.maze_grid == level_b.maze.maze_grid
    assert level_a.pacgums == level_b.pacgums
