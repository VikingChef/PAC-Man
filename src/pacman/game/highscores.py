"""Manage persistent high scores and the cheaters' hall of shame."""

from dataclasses import dataclass


@dataclass
class HighScoreEntry:
    """Represent one player's leaderboard entry."""

    initials: str
    score: int