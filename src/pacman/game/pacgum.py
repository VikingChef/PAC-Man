"""Define the pacgum types used in an active Pac-Man level."""

from enum import Enum, auto


class PacgumType(Enum):
    """Represent the two kinds of pacgum available in the game."""

    # Keep identity separate from scoring and gameplay behaviour.
    PACGUM = auto()
    SUPER_PACGUM = auto()
