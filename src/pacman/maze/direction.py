"""Define movement directions used throughout Pac-Man."""

from enum import Enum


class Direction(Enum):
    """Represent the four movement directions used in the game."""

# Store each direction as horizontal and vertical change.
    NORTH = (0, -1)
    SOUTH = (0, +1)
    EAST = (+1, 0)
    WEST = (-1, 0)
