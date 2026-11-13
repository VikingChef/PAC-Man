
"""Tests for the secret cheat-menu unlock sequence."""

import pygame as pg

from pacman.app.cheat_code import CheatCode


def test_correct_sequence_unlocks_menu() -> None:
    """Unlock only after all seven keys are entered correctly."""

    cheat_code = CheatCode()

    keys = [
        pg.K_UP,
        pg.K_UP,
        pg.K_DOWN,
        pg.K_DOWN,
        pg.K_LEFT,
        pg.K_RIGHT,
        pg.K_c,
    ]

    for index, key in enumerate(keys):
        unlocked = cheat_code.register_key(key, index * 0.5)
        assert unlocked is (index == len(keys) - 1)

    # A successful unlock resets the detector for next time.
    assert cheat_code.progress == 0


def test_sequence_expires_after_one_second() -> None:
    """A gap greater than one second invalidates the sequence."""

    cheat_code = CheatCode()

    cheat_code.register_key(pg.K_UP, 0.0)
    cheat_code.register_key(pg.K_UP, 1.1)

    assert cheat_code.progress == 1


def test_wrong_key_resets_sequence() -> None:
    """An incorrect key discards the current sequence."""

    cheat_code = CheatCode()

    cheat_code.register_key(pg.K_UP, 0.0)
    cheat_code.register_key(pg.K_UP, 0.5)
    cheat_code.register_key(pg.K_RIGHT, 0.8)

    assert cheat_code.progress == 0
