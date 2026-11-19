"""Test game session state and score ownership."""

from pacman.config.models import GameConfig, LevelConfig
from pacman.game.cheat_mode import CheatMode
from pacman.game.game_session import GameSession


def _config() -> GameConfig:
    """Create a minimal session configuration."""
    return GameConfig(
        highscore_filename="highscores.json",
        lives=3,
        pacgum=42,
        points_per_pacgum=10,
        points_per_super_pacgum=50,
        points_per_ghost=200,
        seed=42,
        level_max_time=90,
        levels=[LevelConfig(number=1, width=21, height=21)],
    )


def test_session_starts_without_level() -> None:
    """A session creates a new run only when requested."""
    session = GameSession(_config())
    assert session.game_state is None
    assert session.active_level is None
    session.start_run()
    assert session.game_state is not None
    assert session.game_state.score == 0
    assert session.game_state.lives == 3


def test_session_scoring_and_invalidation() -> None:
    """Points belong to the active run and cheats invalidate them."""
    session = GameSession(_config())
    session.start_run()
    session.award_points(CheatMode(), 10)
    assert session.game_state is not None
    assert session.game_state.score == 10
    session.invalidate_score()
    assert session.game_state.score == 0


def test_session_advancing_final_level_reports_completion() -> None:
    """Advance reports completion without altering the final level."""
    session = GameSession(_config())
    session.start_run()
    assert session.advance_level() is None
    assert session.game_state is not None
    assert session.game_state.current_level == 1


def test_restart_discards_only_current_level_points() -> None:
    """A restart keeps completed-level points and remaining lives."""
    config = _config()
    config.levels.append(LevelConfig(number=2, width=21, height=21))
    session = GameSession(config)
    session.start_run()
    assert session.game_state is not None
    cheat_mode = CheatMode()

    session.award_points(cheat_mode, 2450)
    assert session.advance_level() is not None
    session.award_points(cheat_mode, 730)
    session.game_state.lives = 2

    session.restart_level()
    assert session.game_state.score == 2450
    assert session.game_state.lives == 2
    assert session.game_state.current_level == 2

    session.award_points(cheat_mode, 120)
    session.restart_level()
    assert session.game_state.score == 2450


def test_restart_after_cheat_cannot_restore_invalidated_points() -> None:
    """Restarting cannot recover a score invalidated by cheats."""
    config = _config()
    config.levels.append(LevelConfig(number=2, width=21, height=21))
    session = GameSession(config)
    session.start_run()
    assert session.game_state is not None

    session.award_points(CheatMode(), 2450)
    assert session.advance_level() is not None
    session.invalidate_score()
    session.restart_level()

    assert session.game_state.score == 0


def test_new_run_clears_old_level_checkpoint() -> None:
    """A new game cannot inherit the previous game's score."""
    config = _config()
    config.levels.append(LevelConfig(number=2, width=21, height=21))
    session = GameSession(config)
    session.start_run()
    session.award_points(CheatMode(), 100)
    assert session.advance_level() is not None

    session.start_run()
    session.award_points(CheatMode(), 20)
    session.restart_level()
    assert session.game_state is not None
    assert session.game_state.score == 0
