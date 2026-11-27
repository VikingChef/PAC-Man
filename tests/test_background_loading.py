
"""Verify progressive background playback and safe GIF discovery."""

from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pygame as pg
import pytest

from pacman.app import application as application_module
from pacman.app.app_display import AppDisplay, background_frame_filenames
from pacman.app.application import PacManApp
from pacman.app.menu_renderer import background_frame_index


def test_background_filenames_ignore_unrelated_files(
    tmp_path: Path,
) -> None:
    """Ignore Finder metadata and sort numbered GIFs numerically."""
    for name in (
        ".DS_Store",
        "frame_110.gif",
        "frame_21.gif",
        "frame_100.gif",
        "frame_notes.gif",
        "frame_50.png",
    ):
        (tmp_path / name).touch()

    assert background_frame_filenames(str(tmp_path)) == [
        "frame_21.gif",
        "frame_100.gif",
        "frame_110.gif",
    ]


def test_background_clock_starts_with_first_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Start both animations once, while remaining GIFs still load."""
    app = PacManApp.__new__(PacManApp)
    frame_one = pg.Surface((1, 1))
    frame_two = pg.Surface((1, 1))

    # Simulate background loading without creating an actual window.
    app.display = cast(
        AppDisplay,
        SimpleNamespace(
            frame_gen=iter((frame_one, frame_two)),
            bg=[],
            bg_files=2,
        ),
    )
    app.start_time = 0.0

    # Provide predictable timestamps for the loading sequence.
    now = iter((12.0, 14.0))
    monkeypatch.setattr(
        application_module.time,
        "time",
        lambda: next(now),
    )

    # The first frame starts the animation clock.
    app._load_bg()
    assert app.start_time == 12000.0
    assert len(app.display.bg) == 1

    # Subsequent frames must not reset the original start time.
    app._load_bg()
    assert app.start_time == 12000.0
    assert len(app.display.bg) == 2

    # Exhausting the generator must not restart the animation.
    app._load_bg()
    assert app.start_time == 12000.0


def test_background_frame_selection_does_not_reverse_on_append() -> None:
    """Keep the frame index stable as the available sequence grows."""
    assert background_frame_index(300.0, 5, 90) == 3
    assert background_frame_index(300.0, 6, 90) == 3
    assert background_frame_index(500.0, 4, 90) == 3
    assert background_frame_index(500.0, 7, 90) == 5
    assert background_frame_index(9000.0, 90, 90) == 0
    assert background_frame_index(0.0, 0, 90) == 0
