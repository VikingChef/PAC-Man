
"""Test the Hall of Fame and cheaters' leaderboard."""

import json
from pathlib import Path

import pytest

from pacman.game.highscores import (
    HighScoreEntry,
    HighScoreManager,
    ShameEntry,
    ShameScoreManager,
)


def test_founding_high_scores(tmp_path: Path) -> None:
    """Start with the ten founding Hall of Fame scores."""
    manager = HighScoreManager(str(tmp_path / "scores.json"))

    assert len(manager.high_scores) == 10
    assert manager.high_scores[0] == HighScoreEntry("ASS", 5000)
    assert manager.high_scores[-1] == HighScoreEntry("HOE", 620)
    assert manager.save_blocked is False


def test_founding_shame_entries(tmp_path: Path) -> None:
    """Start with the ten founding Hall of Shame names."""
    manager = HighScoreManager(str(tmp_path / "scores.json"))

    assert len(manager.shame_manager.shame_entries) == 10
    assert manager.shame_manager.shame_entries[0].name == "ROBBIE"
    assert manager.shame_manager.shame_entries[-1].name == "JASMINE"


def test_score_qualification(tmp_path: Path) -> None:
    """Accept scores equal to or above the tenth-place score."""
    manager = HighScoreManager(str(tmp_path / "scores.json"))

    assert manager.qualifies(619) is False
    assert manager.qualifies(620) is True
    assert manager.qualifies(621) is True


def test_reject_low_score(tmp_path: Path) -> None:
    """Leave the leaderboard unchanged for low scores."""
    file_path = tmp_path / "scores.json"
    manager = HighScoreManager(str(file_path))
    original_scores = manager.high_scores.copy()

    manager.add_score(HighScoreEntry("LOW", 619))

    assert manager.high_scores == original_scores
    assert not file_path.exists()


def test_accept_high_score(tmp_path: Path) -> None:
    """Insert a high score and retain only ten entries."""
    manager = HighScoreManager(str(tmp_path / "scores.json"))

    manager.add_score(HighScoreEntry("WIN", 6000))

    assert manager.high_scores[0] == HighScoreEntry("WIN", 6000)
    assert len(manager.high_scores) == 10
    assert HighScoreEntry("HOE", 620) not in manager.high_scores


def test_newer_entry_wins_equal_score(tmp_path: Path) -> None:
    """Place a new tied score ahead of the older entry."""
    manager = HighScoreManager(str(tmp_path / "scores.json"))

    manager.add_score(HighScoreEntry("NEW", 620))

    assert len(manager.high_scores) == 10
    assert manager.high_scores[-1] == HighScoreEntry("NEW", 620)
    assert HighScoreEntry("HOE", 620) not in manager.high_scores


def test_existing_tie_order_is_stable(tmp_path: Path) -> None:
    """Keep the newest entry first when several scores tie."""
    manager = HighScoreManager(str(tmp_path / "scores.json"))

    manager.add_score(HighScoreEntry("ONE", 5000))
    manager.add_score(HighScoreEntry("TWO", 5000))

    assert manager.high_scores[:3] == [
        HighScoreEntry("TWO", 5000),
        HighScoreEntry("ONE", 5000),
        HighScoreEntry("ASS", 5000),
    ]


def test_save_and_reload_high_scores(tmp_path: Path) -> None:
    """Restore legitimate scores after creating a new manager."""
    file_path = tmp_path / "scores.json"
    manager = HighScoreManager(str(file_path))
    manager.add_score(HighScoreEntry("WIN", 7500))

    restored = HighScoreManager(str(file_path))

    assert restored.high_scores == manager.high_scores
    assert restored.save_blocked is False


def test_record_cheater_saves_automatically(tmp_path: Path) -> None:
    """Persist a cheater without awarding legitimate points."""
    file_path = tmp_path / "scores.json"
    manager = HighScoreManager(str(file_path))
    original_scores = manager.high_scores.copy()

    manager.record_cheater(ShameEntry("WANDA"))

    assert file_path.exists()
    assert manager.high_scores == original_scores
    assert manager.shame_manager.shame_entries[0].name == "WANDA"

    restored = HighScoreManager(str(file_path))

    assert restored.shame_manager.shame_entries[0].name == "WANDA"
    assert restored.high_scores == original_scores


def test_shame_history_is_preserved() -> None:
    """Show ten recent cheaters without deleting older history."""
    manager = ShameScoreManager()

    for number in range(15):
        manager.add_cheater(ShameEntry(f"QUEEN{number}"))

    assert len(manager.shame_entries) == 25
    assert len(manager.recent_cheaters()) == 10
    assert manager.recent_cheaters()[0].name == "QUEEN14"
    assert manager.recent_cheaters()[-1].name == "QUEEN5"
    assert manager.shame_entries[-1].name == "JASMINE"


def test_full_shame_history_survives_reload(tmp_path: Path) -> None:
    """Retain all historical cheaters after saving and loading."""
    file_path = tmp_path / "scores.json"
    manager = HighScoreManager(str(file_path))

    for number in range(15):
        manager.record_cheater(ShameEntry(f"QUEEN{number}"))

    restored = HighScoreManager(str(file_path))

    assert len(restored.shame_manager.shame_entries) == 25
    assert restored.shame_manager.recent_cheaters()[0].name == (
        "QUEEN14"
    )


def test_corrupt_json_blocks_saving(tmp_path: Path) -> None:
    """Protect damaged JSON instead of overwriting the file."""
    file_path = tmp_path / "scores.json"
    original_content = "{this is not valid json"
    file_path.write_text(original_content, encoding="utf-8")

    manager = HighScoreManager(str(file_path))

    assert manager.save_blocked is True
    assert manager.high_scores[0] == HighScoreEntry("ASS", 5000)

    manager.add_score(HighScoreEntry("WIN", 9000))
    manager.record_cheater(ShameEntry("WANDA"))

    assert file_path.read_text(encoding="utf-8") == (
        original_content
    )


def test_invalid_utf8_blocks_saving(tmp_path: Path) -> None:
    """Protect save files containing invalid UTF-8 bytes."""
    file_path = tmp_path / "scores.json"
    file_path.write_bytes(b"\xff\xfe")

    manager = HighScoreManager(str(file_path))

    assert manager.save_blocked is True
    manager.save()
    assert file_path.read_bytes() == b"\xff\xfe"


@pytest.mark.parametrize(
    "field, replacement",
    [
        ("high_scores", []),
        ("high_scores", "not a list"),
        ("shame_entries", "not a list"),
    ],
)
def test_invalid_board_structure(
    tmp_path: Path,
    field: str,
    replacement: object,
) -> None:
    """Reject files whose leaderboard structure is invalid."""
    file_path = tmp_path / "scores.json"
    original = HighScoreManager(str(file_path))
    original.save()

    data = json.loads(file_path.read_text(encoding="utf-8"))
    data[field] = replacement
    file_path.write_text(json.dumps(data), encoding="utf-8")

    manager = HighScoreManager(str(file_path))

    assert manager.save_blocked is True
    assert manager.high_scores[0] == HighScoreEntry("ASS", 5000)


@pytest.mark.parametrize(
    "initials, score",
    [
        ("AB", 1000),
        ("abcd", 1000),
        ("abc", 1000),
        ("ÄBC", 1000),
        ("A1C", 1000),
        ("ABC", -1),
        ("ABC", True),
        ("ABC", "1000"),
    ],
)
def test_invalid_high_score_records(
    tmp_path: Path,
    initials: str,
    score: object,
) -> None:
    """Reject invalid initials and score values on loading."""
    file_path = tmp_path / "scores.json"
    manager = HighScoreManager(str(file_path))
    manager.save()

    data = json.loads(file_path.read_text(encoding="utf-8"))
    data["high_scores"][0] = {
        "initials": initials,
        "score": score,
    }
    file_path.write_text(json.dumps(data), encoding="utf-8")

    restored = HighScoreManager(str(file_path))

    assert restored.save_blocked is True
    assert restored.high_scores[0] == HighScoreEntry("ASS", 5000)


def test_unsorted_scores_are_rejected(tmp_path: Path) -> None:
    """Reject saved rankings that are not highest first."""
    file_path = tmp_path / "scores.json"
    manager = HighScoreManager(str(file_path))
    manager.save()

    data = json.loads(file_path.read_text(encoding="utf-8"))
    data["high_scores"][0], data["high_scores"][1] = (
        data["high_scores"][1],
        data["high_scores"][0],
    )
    file_path.write_text(json.dumps(data), encoding="utf-8")

    restored = HighScoreManager(str(file_path))

    assert restored.save_blocked is True
    assert restored.high_scores[0] == HighScoreEntry("ASS", 5000)


@pytest.mark.parametrize("name", ["", "ABCDEFGHIJK", 123])
def test_invalid_shame_names(
    tmp_path: Path,
    name: object,
) -> None:
    """Reject empty, excessively long, or non-string names."""
    file_path = tmp_path / "scores.json"
    manager = HighScoreManager(str(file_path))
    manager.save()

    data = json.loads(file_path.read_text(encoding="utf-8"))
    data["shame_entries"][0] = {"name": name}
    file_path.write_text(json.dumps(data), encoding="utf-8")

    restored = HighScoreManager(str(file_path))

    assert restored.save_blocked is True
    assert restored.shame_manager.shame_entries[0].name == "ROBBIE"
