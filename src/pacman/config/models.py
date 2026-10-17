"""Configuration data models for Pac-Man."""

from dataclasses import dataclass


@dataclass
class LevelConfig:
    """Configuration values for a single Pac-Man level"""

    number: int
    width: int
    height: int


@dataclass
class GameConfig:
    """Configuration values for the Pac-Man game."""

    highscore_filename: str
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
    levels: list[LevelConfig]
