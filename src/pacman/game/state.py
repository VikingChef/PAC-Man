"""Game state for an active Pac-Man run."""

from dataclasses import dataclass


@dataclass
class GameState:
    """Store run-specific Pac-Man game state."""

    # Track the player's current run data.
    score: int
    lives: int
    current_level: int
    remaining_time: int
