"""Shared application test setup and collision fixtures."""

import pygame as pg
from pacman.app.actions import CharSelectAction
from pacman.app.application import AppState, PacManApp
from pacman.config.models import GameConfig, LevelConfig
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall
from pacman.game.cheat_mode import CheatMode
from pacman.game.ghost import Ghost, GhostIdentity, GhostState
from pacman.game.level import Level
from pacman.game.player import Player
from pacman.game.state import GameState
from pacman.app.sprite_animator import SpriteAnimator
from pacman.game.game_session import GameSession


def _test_config() -> GameConfig:
    """Return a valid configuration for application tests."""
    # Build a minimal valid configuration without using the JSON loader.
    return GameConfig(
        highscore_filename="highscores.json",
        lives=3,
        pacgum=42,
        points_per_pacgum=10,
        points_per_super_pacgum=50,
        points_per_ghost=200,
        seed=42,
        level_max_time=90,
        levels=[
            LevelConfig(
                number=1,
                width=21,
                height=21,
            )
        ],
    )


def _start_test_game(app: PacManApp) -> None:
    """Choose a test character before starting the gameplay run."""
    # Application tests start gameplay directly instead of clicking through
    # the character selection screen. Supply the same valid choice the UI
    # would normally provide, while keeping character selection required.
    app.change_queen(CharSelectAction.WAKA_WAKA_WANDA)
    app.start_new_game()


def create_collision_test_app(
    ghost_states: list[GhostState],
    lives: int = 3,
) -> PacManApp:
    """Build a logic-only application with ghosts occupying Pac-Man's cell."""
    # Avoid initializing a Pygame window; the resolver does not need one.
    app = PacManApp.__new__(PacManApp)
    app.config = _test_config()
    app.session = GameSession(app.config)
    app.cheat_mode = CheatMode()
    app.game_state = GameState(score=0, lives=lives, current_level=1)
    app.state = AppState.PLAYING
    # Collision tests only need the animation state, not a display.
    app.sprite_animator = SpriteAnimator(pg.Surface((16, 16)))

    maze = Maze([
        [Wall.NONE for _ in range(3)]
        for _ in range(3)
    ])
    player = Player(
        spawn_position=(1, 1),
        spawn_direction=Direction.EAST,
    )
    identities = list(GhostIdentity)
    ghosts: list[Ghost] = []

    for index, state in enumerate(ghost_states):
        ghost = Ghost(
            spawn_position=(1, 1),
            identity=identities[index],
            spawn_direction=Direction.WEST,
        )
        ghost.state = state
        ghosts.append(ghost)

    app.active_level = Level(
        config=LevelConfig(number=1, width=3, height=3),
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=90,
        pacgums={},
    )
    return app
