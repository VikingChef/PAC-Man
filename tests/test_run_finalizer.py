
"""Test run finalization and leaderboard submissions."""

from pathlib import Path

from pacman.game.highscores import (
    HighScoreEntry,
    HighScoreManager,
)
from pacman.game.run_finalizer import EntryKind, RunFinalizer


def make_finalizer(tmp_path: Path) -> RunFinalizer:
    """Create an isolated finalizer for each test."""
    manager = HighScoreManager(str(tmp_path / "scores.json"))
    return RunFinalizer(manager)


def test_new_finalizer_has_no_active_run(tmp_path: Path) -> None:
    """Start without a run or pending submission."""
    finalizer = make_finalizer(tmp_path)

    assert finalizer.run_active is False
    assert finalizer.run_finalized is False
    assert finalizer.pending_kind is None
    assert finalizer.pending_score is None


def test_qualifying_run_requests_fame(tmp_path: Path) -> None:
    """Request initials when a legitimate score qualifies."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()

    assert finalizer.finish_run(6000, cheats_used=False) is True
    assert finalizer.pending_kind == EntryKind.FAME
    assert finalizer.pending_score == 6000


def test_low_score_needs_no_entry(tmp_path: Path) -> None:
    """Ignore legitimate scores below tenth place."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()

    assert finalizer.finish_run(100, cheats_used=False) is False
    assert finalizer.pending_kind is None
    assert finalizer.run_finalized is True


def test_equal_score_qualifies(tmp_path: Path) -> None:
    """Allow a score matching tenth place to qualify."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()

    assert finalizer.finish_run(620, cheats_used=False) is True
    assert finalizer.pending_kind == EntryKind.FAME


def test_cheater_requests_shame(tmp_path: Path) -> None:
    """Prioritize cheating regardless of the final score."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()

    assert finalizer.finish_run(9000, cheats_used=True) is True
    assert finalizer.pending_kind == EntryKind.SHAME
    assert finalizer.pending_score is None


def test_abandoned_cheater_requests_shame(tmp_path: Path) -> None:
    """Record cheaters who abandon their runs."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()

    assert finalizer.finish_run(
        0,
        cheats_used=True,
        abandoned=True,
    ) is True

    assert finalizer.pending_kind == EntryKind.SHAME


def test_abandoned_legitimate_run_is_ignored(tmp_path: Path) -> None:
    """Avoid awarding fame for an abandoned run."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()

    assert finalizer.finish_run(
        9000,
        cheats_used=False,
        abandoned=True,
    ) is False

    assert finalizer.pending_kind is None


def test_run_cannot_finalize_twice(tmp_path: Path) -> None:
    """Prevent duplicate endings from changing pending results."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()

    assert finalizer.finish_run(7000, False) is True
    assert finalizer.finish_run(0, True) is False

    assert finalizer.pending_kind == EntryKind.FAME
    assert finalizer.pending_score == 7000


def test_no_run_cannot_finalize(tmp_path: Path) -> None:
    """Ignore finalization before gameplay begins."""
    finalizer = make_finalizer(tmp_path)

    assert finalizer.finish_run(9000, False) is False


def test_valid_fame_submission(tmp_path: Path) -> None:
    """Save valid initials and clear the pending entry."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()
    finalizer.finish_run(6000, False)

    assert finalizer.submit_name("abc") is True
    assert finalizer.high_scores.high_scores[0] == (
        HighScoreEntry("ABC", 6000)
    )
    assert finalizer.pending_kind is None
    assert finalizer.pending_score is None


def test_invalid_fame_submission(tmp_path: Path) -> None:
    """Retain pending entry when initials are invalid."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()
    finalizer.finish_run(6000, False)

    assert finalizer.submit_name("AB") is False
    assert finalizer.submit_name("A1C") is False
    assert finalizer.submit_name("ÄBC") is False

    assert finalizer.pending_kind == EntryKind.FAME
    assert finalizer.pending_score == 6000


def test_valid_shame_submission(tmp_path: Path) -> None:
    """Save a cheater's name without adding a legitimate score."""
    finalizer = make_finalizer(tmp_path)
    original_scores = finalizer.high_scores.high_scores.copy()

    finalizer.start_run()
    finalizer.finish_run(0, True)

    assert finalizer.submit_name("wanda") is True
    assert finalizer.high_scores.shame_manager.shame_entries[0].name == (
        "WANDA"
    )
    assert finalizer.high_scores.high_scores == original_scores


def test_invalid_shame_submission(tmp_path: Path) -> None:
    """Reject empty and excessively long cheater names."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()
    finalizer.finish_run(0, True)

    assert finalizer.submit_name("   ") is False
    assert finalizer.submit_name("ABCDEFGHIJK") is False
    assert finalizer.pending_kind == EntryKind.SHAME


def test_submission_cannot_repeat(tmp_path: Path) -> None:
    """Reject a second submission after the first succeeds."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()
    finalizer.finish_run(0, True)

    assert finalizer.submit_name("WANDA") is True
    assert finalizer.submit_name("WANDA") is False

    names = finalizer.high_scores.shame_manager.shame_entries
    assert sum(entry.name == "WANDA" for entry in names) == 1


def test_new_run_resets_finalization(tmp_path: Path) -> None:
    """Allow a fresh game to create another leaderboard entry."""
    finalizer = make_finalizer(tmp_path)
    finalizer.start_run()
    finalizer.finish_run(0, True)
    finalizer.submit_name("WANDA")

    finalizer.start_run()

    assert finalizer.run_active is True
    assert finalizer.run_finalized is False
    assert finalizer.pending_kind is None
    assert finalizer.finish_run(7000, False) is True
