
"""Manage scoring rules for the current game."""

from pacman.game.cheat_mode import CheatMode
from pacman.game.state import GameState


def invalidate_score(game_state: GameState | None) -> None:
    """Reset the score when a cheat is activated."""
    if game_state is not None:
        game_state.score = 0


def award_points(
    game_state: GameState | None,
    cheat_mode: CheatMode,
    points: int,
) -> None:
    """Award points according to the current scoring rules."""
    if game_state is None:
        return

    # Once a cheat has been used, scoring remains disabled.
    if cheat_mode.cheats_used:
        return

    # Disco Mode doubles points without invalidating the score.
    multiplier = 2 if cheat_mode.disco_enabled else 1

    game_state.score += points * multiplier
