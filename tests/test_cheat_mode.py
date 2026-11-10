"""Tests for Pac-Man cheat settings."""

import pytest

from pacman.game.cheat_mode import CheatMode


def test_cheats_start_disabled() -> None:
    """Verify that all cheats start disabled."""

    # Create cheat setting with default values.
    cheat_mode = CheatMode()

    # Assert that all cheat modes are off at start.
    assert cheat_mode.invincible is False
    assert cheat_mode.ghosts_frozen is False
    assert cheat_mode.disco_enabled is False
    assert cheat_mode.timer_stopped is False
    assert cheat_mode.cheats_used is False
    assert cheat_mode.being_fabulous is False


def test_toggle_invincibility() -> None:
    """Verify that invincibility can be enabled and disabled."""
    # Create cheat settings with default values.
    cheat_mode = CheatMode()

    # Enable invincibility.
    cheat_mode.toggle_invincibility()
    assert cheat_mode.invincible is True

    # Disable invincibility.
    cheat_mode.toggle_invincibility()
    assert cheat_mode.invincible is False


def test_toggle_ghosts_frozen() -> None:
    """Verify that ghost movement can be frozen and unfrozen."""
    # Create cheat settings with default values.
    cheat_mode = CheatMode()

    # Freeze ghost movement.
    cheat_mode.toggle_ghost_freeze()
    assert cheat_mode.ghosts_frozen is True

    # Restore ghost movement.
    cheat_mode.toggle_ghost_freeze()
    assert cheat_mode.ghosts_frozen is False


def test_toggle_disco_enabled() -> None:
    """Verify that disco mode can be enabled and disabled."""
    # Create cheat settings with default values.
    cheat_mode = CheatMode()

    # Activate disco mode.
    cheat_mode.toggle_disco_enabled()
    assert cheat_mode.disco_enabled is True

    # Deactivate disco mode.
    cheat_mode.toggle_disco_enabled()
    assert cheat_mode.disco_enabled is False


def test_toggle_timer_stopped() -> None:
    """Verify that the timer can be frozen and unfrozen."""
    # Create cheat settings with default values.
    cheat_mode = CheatMode()

    # Freeze the countdown timer.
    cheat_mode.toggle_timer_stopped()
    assert cheat_mode.timer_stopped is True

    # Restore the countdown timer.
    cheat_mode.toggle_timer_stopped()
    assert cheat_mode.timer_stopped is False


def test_disco_preserves_cheat_history() -> None:
    """Verify that disco mode cannot erase previous cheating."""
    # Create fresh cheat settings.
    cheat_mode = CheatMode()

    # Activate invincibility to mark the run as cheat-assisted.
    cheat_mode.toggle_invincibility()

    # Activate disco mode afterward.
    cheat_mode.toggle_disco_enabled()

    # Disco mode must not erase the previous cheat.
    assert cheat_mode.cheats_used is True
    assert cheat_mode.disco_enabled is True
    assert cheat_mode.being_fabulous is True


def test_disco_alone_does_not_count_as_cheating() -> None:
    """Verify that disco mode alone keeps the run eligible."""
    # Create fresh cheat settings.
    cheat_mode = CheatMode()

    # Activate disco mode without gameplay cheats.
    cheat_mode.toggle_disco_enabled()

    # Fabulousness alone must not invalidate the score.
    assert cheat_mode.disco_enabled is True
    assert cheat_mode.being_fabulous is True
    assert cheat_mode.cheats_used is False


def test_disabling_invincibility_preserves_cheat_history() -> None:
    """Verify that disabling invincibility does not erase cheating."""
    # Create fresh cheat settings.
    cheat_mode = CheatMode()

    # Enable and then disable invincibility.
    cheat_mode.toggle_invincibility()
    cheat_mode.toggle_invincibility()

    # Invincibility is off, but the run remains cheat-assisted.
    assert cheat_mode.invincible is False
    assert cheat_mode.cheats_used is True


@pytest.mark.parametrize(
    "toggle_method",
    ["toggle_ghost_freeze", "toggle_timer_stopped"],
)
def test_freeze_cheat_history(
    toggle_method: str,
) -> None:
    """Verify that freeze cheats preserve cheat history."""

    # Create fresh cheat settings.
    cheat_mode = CheatMode()

    method = getattr(cheat_mode, toggle_method)
    method()

    assert cheat_mode.cheats_used is True

    method()

    assert cheat_mode.cheats_used is True
