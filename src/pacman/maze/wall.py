"""Define our internal representation of the walls around a maze position."""

from enum import IntFlag, auto


class Wall(IntFlag):
    """Represent the walls around a maze position."""

# Define combinable wall flags, with NONE representing no walls.
    NONE = 0
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()
