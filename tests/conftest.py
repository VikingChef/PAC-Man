"""Configure the test environment for Pac-Man."""

import os


# Prevent pygame tests from taking over the real display.
os.environ["SDL_VIDEODRIVER"] = "dummy"
