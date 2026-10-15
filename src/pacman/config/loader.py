"""Load and validate Pac-Man configuration data."""

import json
import logging
from pathlib import Path

from pacman.config.models import GameConfig, LevelConfig

logger = logging.getLogger(__name__)

DEFAULT_LEVEL_COUNT = 10
DEFAULT_LEVEL_WIDTH = 21
DEFAULT_LEVEL_HEIGHT = 21


def _default_levels() -> list[LevelConfig]:
    """Return the default Pac-Man level configuration."""

    return [
        LevelConfig(
            number=number,
            width=DEFAULT_LEVEL_WIDTH,
            height=DEFAULT_LEVEL_HEIGHT,
        )
        for number in range(1, DEFAULT_LEVEL_COUNT + 1)
    ]


def load_config(config_path: Path) -> GameConfig:
    """Load and validate a Pac-Man configuration file."""

    # File might not exist or be readable.
    try:
        config_text = config_path.read_text()
    except OSError as error:
        raise RuntimeError(
            f"Could not read configuration file: {error}"
        ) from error

    # JSON does not support the comment lines allowed by the subject.
    clean_text = "\n".join(
        line for line in config_text.splitlines()
        if not line.lstrip().startswith("#")
    )

    # Parse the cleaned JSON text.
    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Invalid configuration JSON: {error}"
        ) from error

    # The configuration root must be a JSON object.
    if not isinstance(data, dict):
        raise RuntimeError(
            "Configuration root must be a JSON object."
        )

    highscore_filename = data.get(
        "highscore_filename",
        "highscores.json",
    )

    # Validate the highscore filename.
    if (
        not isinstance(highscore_filename, str)
        or not highscore_filename.strip()
    ):
        logger.warning(
            "Invalid highscore_filename. Using default: highscores.json"
        )
        highscore_filename = "highscores.json"

    lives = data.get("lives", 3)

    # Validate the number of lives.
    if not isinstance(lives, int) or lives <= 0:
        logger.warning(
            "Invalid lives value. Using default: 3"
        )
        lives = 3

    pacgum = data.get("pacgum", 42)

    # Validate the number of pacgums.
    if not isinstance(pacgum, int) or pacgum <= 0:
        logger.warning(
            "Invalid pacgum count. Using default: 42"
        )
        pacgum = 42

    points_per_pacgum = data.get("points_per_pacgum", 10)

    # Validate points awarded for a pacgum.
    if (
        not isinstance(points_per_pacgum, int)
        or points_per_pacgum <= 0
    ):
        logger.warning(
            "Invalid pacgum point count. Using default: 10"
        )
        points_per_pacgum = 10

    points_per_super_pacgum = data.get(
        "points_per_super_pacgum",
        50,
    )

    # Validate points awarded for a super pacgum.
    if (
        not isinstance(points_per_super_pacgum, int)
        or points_per_super_pacgum <= 0
    ):
        logger.warning(
            "Invalid super pacgum point count. Using default: 50"
        )
        points_per_super_pacgum = 50

    points_per_ghost = data.get("points_per_ghost", 200)

    # Validate points awarded for a ghost.
    if (
        not isinstance(points_per_ghost, int)
        or points_per_ghost <= 0
    ):
        logger.warning(
            "Invalid ghost point count. Using default: 200"
        )
        points_per_ghost = 200

    seed = data.get("seed", 42)

    # Validate the maze seed.
    if not isinstance(seed, int):
        logger.warning(
            "Invalid seed value. Using default: 42"
        )
        seed = 42

    level_max_time = data.get("level_max_time", 90)

    # Validate the level timer.
    if not isinstance(level_max_time, int) or level_max_time <= 0:
        logger.warning(
            "Invalid level_max_time value. Using default: 90"
        )
        level_max_time = 90

    levels_data = data.get("levels", [])

    levels: list[LevelConfig]

    # Validate that the levels value is a non-empty list.
    if not isinstance(levels_data, list) or not levels_data:
        logger.warning(
            "Invalid or empty levels value. Using default levels."
        )
        levels = _default_levels()
    else:
        levels = []

        # Validate each configured level entry.
        for index, level_data in enumerate(levels_data, start=1):

            # Replace invalid level entries with safe defaults.
            if not isinstance(level_data, dict):
                logger.warning(
                    f"Invalid level {index} entry. "
                    "Using default dimensions."
                )
                levels.append(
                    LevelConfig(
                        number=index,
                        width=DEFAULT_LEVEL_WIDTH,
                        height=DEFAULT_LEVEL_HEIGHT,
                    )
                )
                continue

            # Read values and use defaults for missing keys.
            number = level_data.get("number", index)
            width = level_data.get(
                "width",
                DEFAULT_LEVEL_WIDTH,
            )
            height = level_data.get(
                "height",
                DEFAULT_LEVEL_HEIGHT,
            )

            # Validate the level number.
            if not isinstance(number, int) or number <= 0:
                logger.warning(
                    f"Invalid number for level {index}. "
                    f"Using default: {index}"
                )
                number = index

            # Validate maze width.
            if not isinstance(width, int) or width <= 0:
                logger.warning(
                    f"Invalid width for level {index}. "
                    f"Using default: {DEFAULT_LEVEL_WIDTH}"
                )
                width = DEFAULT_LEVEL_WIDTH

            # Validate maze height.
            if not isinstance(height, int) or height <= 0:
                logger.warning(
                    f"Invalid height for level {index}. "
                    f"Using default: {DEFAULT_LEVEL_HEIGHT}"
                )
                height = DEFAULT_LEVEL_HEIGHT

            # Build a LevelConfig from the cleaned values.
            levels.append(
                LevelConfig(
                    number=number,
                    width=width,
                    height=height,
                )
            )

    # Ensure that the game always has at least 10 levels.
    if len(levels) < DEFAULT_LEVEL_COUNT:
        logger.warning(
            "Fewer than 10 levels configured. "
            "Adding default levels."
        )

        for number in range(
            len(levels) + 1,
            DEFAULT_LEVEL_COUNT + 1,
        ):
            levels.append(
                LevelConfig(
                    number=number,
                    width=DEFAULT_LEVEL_WIDTH,
                    height=DEFAULT_LEVEL_HEIGHT,
                )
            )

    # Build the final validated game configuration.
    return GameConfig(
        highscore_filename=highscore_filename,
        lives=lives,
        pacgum=pacgum,
        points_per_pacgum=points_per_pacgum,
        points_per_super_pacgum=points_per_super_pacgum,
        points_per_ghost=points_per_ghost,
        seed=seed,
        level_max_time=level_max_time,
        levels=levels,
    )
