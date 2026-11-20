"""Test game session state and score ownership."""

from pacman.config.models import GameConfig, LevelConfig
from pacman.game.cheat_mode import CheatMode
from pacman.game.game_session import GameSession
from pacman.app.actions import CharSelectAction
from pacman.app.maze_view import build_maze_layout
from pacman.game.level_factory import create_level


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


def test_mercy_can_only_be_granted_once() -> None:
    """Grant three lives once without losing completed-level points."""
    config = _config()
    config.levels.append(LevelConfig(number=2, width=21, height=21))

    session = GameSession(config)
    session.start_run()
    assert session.game_state is not None

    # Complete level one and establish its permanent score.
    session.award_points(CheatMode(), 2450)
    assert session.advance_level() is not None

    # Lose the last life after earning points on level two.
    session.award_points(CheatMode(), 730)
    session.game_state.lives = 0

    # The first plea restores lives and the level score checkpoint.
    assert session.request_mercy() is True
    assert session.game_state.lives == 3
    assert session.game_state.score == 2450
    assert session.game_state.current_level == 2
    assert session.mercy_used is True

    # Simulate another defeat and attempt a second plea.
    session.game_state.lives = 0
    assert session.request_mercy() is False

    # The refusal must not grant lives or change the score.
    assert session.game_state.lives == 0
    assert session.game_state.score == 2450


def test_new_run_restores_mercy_allowance() -> None:
    """Allow one new royal pardon when a fresh run begins."""
    session = GameSession(_config())
    session.start_run()
    assert session.game_state is not None

    # Use the one available pardon.
    session.game_state.lives = 0
    assert session.request_mercy() is True
    assert session.mercy_used is True

    # Starting a fresh game restores the allowance.
    session.start_run()
    assert session.game_state is not None
    assert session.game_state.lives == 3
    assert session.mercy_used is False

    # Mercy cannot be requested while the player is alive.
    assert session.request_mercy() is False


def test_mercy_recreates_the_same_maze() -> None:
    """Mercy must restore the original maze layout."""
    config = _config()
    session = GameSession(config)
    session.start_run()

    level_config = config.levels[0]
    queen = CharSelectAction.WAKA_WAKA_WANDA

    # Generate the original level and remember its layout.
    original_level = session.load_level(
        level_config, 42, queen, create_level
    )
    original_layout = build_maze_layout(original_level)

    assert session.current_level_seed == 42
    assert session.game_state is not None

    # Simulate final defeat and request the royal pardon.
    session.game_state.lives = 0
    assert session.request_mercy() is True

    # Rebuild the level using the seed retained by the session.
    original_seed = session.current_level_seed
    assert original_seed is not None

    restored_level = session.load_level(
        level_config, original_seed, queen, create_level
    )
    restored_layout = build_maze_layout(restored_level)

    assert restored_level is not original_level
    assert restored_layout == original_layout
    assert session.game_state.lives == 3
    assert session.mercy_used is True
