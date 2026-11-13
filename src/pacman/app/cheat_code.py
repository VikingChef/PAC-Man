
"""Recognise the secret keyboard sequence for the cheat menu."""

import pygame as pg


class CheatCode:
    """Track the secret sequence and enforce its timing limit."""

    SEQUENCE = (
        pg.K_UP,
        pg.K_UP,
        pg.K_DOWN,
        pg.K_DOWN,
        pg.K_LEFT,
        pg.K_RIGHT,
        pg.K_c,
    )

    MAX_KEY_INTERVAL = 1.0

    def __init__(self) -> None:
        """Start with no keys entered."""
        self.progress = 0
        self.last_key_time: float | None = None

    def reset(self) -> None:
        """Discard the current sequence."""
        self.progress = 0
        self.last_key_time = None

    def register_key(self, key: int, current_time: float) -> bool:
        """Return True when the complete secret sequence is entered."""

        # An unfinished sequence expires after one second.
        if (
            self.last_key_time is not None
            and current_time - self.last_key_time > self.MAX_KEY_INTERVAL
        ):
            self.reset()

        # Check whether the next key matches the expected key.
        if key == self.SEQUENCE[self.progress]:
            self.progress += 1
            self.last_key_time = current_time

            # A complete sequence unlocks the cheat panel.
            if self.progress == len(self.SEQUENCE):
                self.reset()
                return True

            return False

        # A wrong key resets progress, but it may also be
        # the first key of a new sequence.
        self.reset()

        if key == self.SEQUENCE[0]:
            self.progress = 1
            self.last_key_time = current_time

        return False
