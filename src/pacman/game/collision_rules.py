
"""Resolve ghost collisions and player life loss."""

from enum import Enum, auto

from pacman.game.cheat_mode import CheatMode
from pacman.game.ghost import GhostState
from pacman.game.level import Level
from pacman.game.scoring import award_points
from pacman.game.state import GameState


class CollisionOutcome(Enum):
    """Describe the result of a ghost collision check."""

    NONE = auto()
    PLAYER_CAUGHT = auto()
    GHOST_EATEN = auto()


def resolve_collision(
    level: Level,
    game_state: GameState,
    cheat_mode: CheatMode,
    ghost_points: int,
) -> CollisionOutcome:
    """Apply ghost collision rules and return the outcome."""
    colliding_ghosts = level.check_ghost_collision()

    if not colliding_ghosts:
        return CollisionOutcome.NONE

    # Dangerous ghosts take priority over edible ghosts.
    if any(
        ghost.state == GhostState.ENRAGED
        for ghost in colliding_ghosts
    ):
        if cheat_mode.invincible:
            return CollisionOutcome.NONE

        return CollisionOutcome.PLAYER_CAUGHT

    # Only successfully eaten ghosts award points.
    ate_ghost = False

    for ghost in colliding_ghosts:
        if ghost.eat():
            award_points(
                game_state,
                cheat_mode,
                ghost_points,
            )
            ate_ghost = True

    if ate_ghost:
        return CollisionOutcome.GHOST_EATEN

    return CollisionOutcome.NONE


def lose_life(
    level: Level,
    game_state: GameState,
) -> bool:
    """Deduct a life and report whether the game is over."""
    game_state.lives -= 1

    if game_state.lives <= 0:
        return True

    level.reset_positions()
    return False
