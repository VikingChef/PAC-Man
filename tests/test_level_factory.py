"""Tests for constructing active Pac-Man levels."""

from pathlib import Path
import pytest

from pacman.config.loader import load_config
from pacman.game.ghost_ai import calculate_distances
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


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4, 5, 42, 99])
def test_generated_level_has_reachable_spawns_and_pacgums(
    seed: int,
) -> None:
    """Verify that characters and pacgums share a reachable maze area."""

    # Generate the same first level used by the application.
    config = load_config(Path("config.json"))

    level = create_level(
        config=config.levels[0],
        seed=seed,
        time_limit=config.level_max_time,
        pacgum_count=config.pacgum,
    )

    # Find every cell reachable from the player's spawn.
    distances = calculate_distances(
        level.maze,
        level.player.position,
    )

    # Pac-Man must have somewhere to go.
    assert len(distances) > 1

    # Every ghost and pacgum must be reachable.
    for ghost in level.ghosts:
        assert ghost.position in distances

    for position in level.pacgums:
        assert position in distances
