
"""Manage persistent high scores and the cheaters' hall of shame."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HighScoreEntry:
    """Represent one player's leaderboard entry."""

    initials: str
    score: int


class HighScoreManager:
    """Manage the game's leaderboard."""

    def __init__(self, filename: str = "highscores.json") -> None:
        """Prepare the leaderboard and its save location."""
        self.file_path = Path(filename)

        self.high_scores: list[HighScoreEntry] = [
            HighScoreEntry("ASS", 5000),
            HighScoreEntry("FUK", 4200),
            HighScoreEntry("CNT", 3600),
            HighScoreEntry("BTM", 3000),
            HighScoreEntry("DIC", 2500),
            HighScoreEntry("GAG", 2000),
            HighScoreEntry("TOP", 1500),
            HighScoreEntry("KNK", 1200),
            HighScoreEntry("HNG", 900),
            HighScoreEntry("HOE", 620),
        ]

        # Keep the shame leaderboard alongside legitimate scores.
        self.shame_manager = ShameScoreManager()

        # Prevent damaged existing save files from being overwritten.
        self.save_blocked = False

        # Restore saved records after both leaderboards are initialized.
        self.load()

    def add_score(self, entry: HighScoreEntry) -> None:
        """Add a qualifying score to the leaderboard."""
        # Reject scores below tenth place before changing the board.
        if not self.qualifies(entry.score):
            return

        self.high_scores.insert(0, entry)

        # Stable sorting places newer entries first when scores tie.
        self.high_scores.sort(
            key=lambda entry: entry.score,
            reverse=True,
        )

        self.high_scores = self.high_scores[:10]

        # Persist the updated leaderboard after accepting a new score.
        self.save()

    def record_cheater(self, entry: ShameEntry) -> None:
        """Record a cheater and persist both leaderboards."""
        # Let the shame manager maintain its newest-first history.
        self.shame_manager.add_cheater(entry)

        # Save both leaderboards through our shared persistence method.
        self.save()

    def qualifies(self, score: int) -> bool:
        """Determine if a score qualifies for the top 10."""
        return score >= self.high_scores[9].score

    def save(self) -> None:
        """Save both leaderboards to a JSON file."""
        # Never overwrite an existing file that failed validation.
        if self.save_blocked:
            return

        # Convert our objects into JSON-compatible dictionaries.
        data = {
            "high_scores": [
                {"initials": entry.initials, "score": entry.score}
                for entry in self.high_scores
            ],
            "shame_entries": [
                {"name": entry.name}
                for entry in self.shame_manager.shame_entries
            ],
        }

        # Write to a temporary file first to protect existing scores.
        temporary_path = self.file_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8",
        )

        # Replace the old save only after the new file is complete.
        temporary_path.replace(self.file_path)

    def load(self) -> None:
        """Restore both leaderboards from their saved JSON data."""
        # First launch: keep the founding entries if no file exists.
        if not self.file_path.is_file():
            return

        # Protect an existing file until we know its data is valid.
        self.save_blocked = True

        # A damaged JSON file must not prevent the game from starting.
        try:
            data = json.loads(
                self.file_path.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError):
            return

        # Reject incomplete or unexpected file structures.
        if not isinstance(data, dict):
            return

        scores = data.get("high_scores")
        cheaters = data.get("shame_entries")

        if not isinstance(scores, list):
            return
        if not isinstance(cheaters, list):
            return

        # Rebuild our dataclass objects from the stored dictionaries.
        try:
            high_scores = [
                HighScoreEntry(item["initials"], item["score"])
                for item in scores
            ]
            shame_entries = [
                ShameEntry(item["name"])
                for item in cheaters
            ]
        except (KeyError, TypeError):
            return

        # Reject invalid records before changing either leaderboard.
        if any(
            not isinstance(entry.initials, str)
            or len(entry.initials) != 3
            or not entry.initials.isascii()
            or not entry.initials.isalpha()
            or entry.initials != entry.initials.upper()
            or type(entry.score) is not int
            or entry.score < 0
            for entry in high_scores
        ):
            return

        if any(
            not isinstance(entry.name, str)
            or not 1 <= len(entry.name) <= 10
            for entry in shame_entries
        ):
            return

        # The Hall of Fame must contain exactly ten ranked entries.
        if len(high_scores) != 10:
            return

        # Verify the scores are ordered from highest to lowest.
        if high_scores != sorted(
            high_scores,
            key=lambda entry: entry.score,
            reverse=True,
        ):
            return

        # Only replace the existing boards when all checks pass.
        self.high_scores = high_scores
        self.shame_manager.shame_entries = shame_entries

        # The saved data passed validation, so future writes are safe.
        self.save_blocked = False


@dataclass
class ShameEntry:
    """Represent one entry in the cheaters' leaderboard."""

    name: str


class ShameScoreManager:
    """Manage the cheaters' leaderboard."""

    def __init__(self) -> None:
        """Prepare the leaderboard of shame."""
        self.shame_entries: list[ShameEntry] = [
            ShameEntry("ROBBIE"),
            ShameEntry("SHARON"),
            ShameEntry("TYRA"),
            ShameEntry("GIA"),
            ShameEntry("MILK"),
            ShameEntry("PHI PHI"),
            ShameEntry("SHERRY PIE"),
            ShameEntry("MIMI"),
            ShameEntry("EUREKA"),
            ShameEntry("JASMINE"),
        ]

    def recent_cheaters(self) -> list[ShameEntry]:
        """Return the ten newest cheaters without deleting history."""
        return self.shame_entries[:10]

    def add_cheater(self, entry: ShameEntry) -> None:
        """Record a cheater without discarding earlier entries."""
        # Newest entries come first; the full history is preserved.
        self.shame_entries.insert(0, entry)
