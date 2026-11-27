
"""Manage persistent high scores and the cheaters' hall of shame."""

from __future__ import annotations

import json
import platform
import sys
from dataclasses import dataclass
from pathlib import Path


# Browser saves are tied to this game's website and browser profile.
BROWSER_STORAGE_KEY = "pac_maam_highscores_v1"


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

        # Prevent damaged existing save data from being overwritten.
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

    def _read_saved_text(self) -> str | None:
        """Read saved scores from the current platform."""
        if sys.platform == "emscripten":
            # Browser Python cannot rely on ordinary files persisting.
            # Access the JavaScript window supplied by Pygbag.
            try:
                window = getattr(platform, "window")
                return window.localStorage.getItem(
                    BROWSER_STORAGE_KEY
                )
            except Exception:
                # Avoid replacing a save we cannot safely inspect.
                self.save_blocked = True
                return None

        # On desktop, retain the existing JSON-file behaviour.
        if not self.file_path.is_file():
            return None

        try:
            return self.file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            self.save_blocked = True
            return None

    def _write_saved_text(self, text: str) -> None:
        """Write saved scores using platform-appropriate storage."""
        if sys.platform == "emscripten":
            # localStorage survives ordinary browser page reloads.
            window = getattr(platform, "window")
            window.localStorage.setItem(BROWSER_STORAGE_KEY, text)
            return

        # Keep the desktop save atomic: write first, replace second.
        temporary_path = self.file_path.with_suffix(".tmp")
        temporary_path.write_text(text, encoding="utf-8")
        temporary_path.replace(self.file_path)

    def save(self) -> None:
        """Persist both leaderboards on the current platform."""
        # Never overwrite existing data that failed validation.
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

        # Use the same data format on desktop and in the browser.
        saved_text = json.dumps(data, indent=4)

        try:
            self._write_saved_text(saved_text)
        except (OSError, Exception):
            # A failed save must not crash an otherwise playable game.
            self.save_blocked = True

    def load(self) -> None:
        """Restore both leaderboards from their saved JSON data."""
        saved_text = self._read_saved_text()

        # First launch: keep the founding entries if no save exists.
        if saved_text is None:
            return

        # Protect saved data until we know its contents are valid.
        self.save_blocked = True

        # A damaged save must not prevent the game from starting.
        try:
            data = json.loads(saved_text)
        except (TypeError, ValueError):
            return

        # Reject incomplete or unexpected save structures.
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
