"""Protect the active run when changing its character artwork."""

import pytest
import pygame as pg

from pacman.app.actions import CharSelectAction
from pacman.app.application import AppState, PacManApp
from pacman.app.pause_menu import PauseMenuAction
from pacman.game.player import Player
from pacman.maze.direction import Direction
from tests.app_test_helpers import _start_test_game, _test_config


def test_player_sprite_change_preserves_movement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Replacing artwork must not reset a player's logical state."""
    loaded_paths: list[str] = []

    def fake_load(path: str) -> pg.Surface:
        """Record assets while avoiding a display dependency."""
        loaded_paths.append(path)
        return pg.Surface((8, 8))

    monkeypatch.setattr("pacman.game.player.load_trans_image", fake_load)
    player = Player((3, 4), Direction.NORTH)
    player.position = (6, 7)
    player.direction = Direction.WEST

    player.set_sprite("ms-pellet")

    assert player.position == (6, 7)
    assert player.direction == Direction.WEST
    assert player.spawn_position == (3, 4)
    assert player.spawn_direction == Direction.NORTH
    assert len(loaded_paths) == 3
    assert all("ms-pellet" in path for path in loaded_paths)
    assert set(player.sprite_path) == set(Direction)


def test_pause_change_queen_preserves_active_level() -> None:
    """Switching Queen must preserve every part of the current run."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    assert app.active_level is not None
    assert app.game_state is not None

    level = app.active_level
    player = level.player
    ghost_objects = tuple(level.ghosts)
    existing_pacgums = dict(level.pacgums)
    player_position = player.position
    existing_lives = app.game_state.lives
    app.game_state.score = 245
    existing_time = level.remaining_time

    app.pause_game()
    app.handle_pause_action(PauseMenuAction.CHANGE_QUEEN)
    assert app.state == AppState.CHAR_SELECT
    assert app.changing_queen is True

    app._handle_char_select_action(CharSelectAction.MS_POWER_PELLET)

    assert app.state == AppState.PLAYING
    assert app.changing_queen is False
    assert app.queen_chosen == CharSelectAction.MS_POWER_PELLET
    assert app.active_level is level
    assert app.active_level.player is player
    assert app.game_state.score == 245
    assert app.game_state.lives == existing_lives
    assert level.remaining_time == existing_time
    assert level.pacgums == existing_pacgums
    assert tuple(level.ghosts) == ghost_objects
    assert player.position == player_position
    assert player.sprite_path[Direction.NORTH] is not None


def test_back_from_queen_change_returns_to_pause() -> None:
    """Back from an in-game Queen change must not abandon the run."""
    app = PacManApp(_test_config())
    _start_test_game(app)
    existing_level = app.active_level
    existing_queen = app.queen_chosen

    app.pause_game()
    app.handle_pause_action(PauseMenuAction.CHANGE_QUEEN)
    app._handle_char_select_action(CharSelectAction.MAIN_MENU)

    assert app.state == AppState.PAUSED
    assert app.changing_queen is False
    assert app.active_level is existing_level
    assert app.queen_chosen == existing_queen
    app.resume_game()
    assert app.state == AppState.PLAYING
