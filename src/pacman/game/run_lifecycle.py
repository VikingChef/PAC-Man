
"""Manage game runs, level progression and timeout life loss."""

from pacman.config.models import GameConfig, LevelConfig
from pacman.game.state import GameState


def create_run(config: GameConfig) -> GameState:
    """Create a fresh run using the configured starting values."""
    return GameState(
        score=0,
        lives=config.lives,
        current_level=1,
    )


def advance_level(
    game_state: GameState,
    config: GameConfig,
) -> LevelConfig | None:
    """Advance the run and return the next level configuration."""
    if game_state.current_level >= len(config.levels):
        return None

    game_state.current_level += 1

    return config.levels[game_state.current_level - 1]


def resolve_timeout(
    game_state: GameState,
    config: GameConfig,
) -> LevelConfig | None:
    """Deduct a life and return the level to restart if alive."""
    game_state.lives -= 1

    if game_state.lives <= 0:
        return None

    return config.levels[game_state.current_level - 1]
