
"""Configure the test environment for Pac-Man."""

import os

# Prevent pygame tests from taking over the real display.
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg  # noqa: E402


def pytest_sessionstart(session: object) -> None:
    """Initialize a dummy display before tests begin."""
    pg.display.init()
    pg.display.set_mode((1, 1))
