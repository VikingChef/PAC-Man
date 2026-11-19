
"""Finalize game runs and coordinate leaderboard submissions."""

from __future__ import annotations

from enum import Enum, auto

from pacman.game.highscores import (
    HighScoreEntry,
    HighScoreManager,
    ShameEntry,
)


class EntryKind(Enum):
    """Identify the leaderboard awaiting player identification."""

    FAME = auto()
    SHAME = auto()


class RunFinalizer:
    """Manage one run's eligibility and leaderboard submission."""

    def __init__(self, high_scores: HighScoreManager) -> None:
        """Prepare the finalizer with shared leaderboard storage."""
        self.high_scores = high_scores
        self.run_active = False
        self.run_finalized = False
        self.pending_kind: EntryKind | None = None
        self.pending_score: int | None = None

    def start_run(self) -> None:
        """Reset submission tracking for a new game."""
        self.run_active = True
        self.run_finalized = False
        self.pending_kind = None
        self.pending_score = None

    def finish_run(
        self,
        score: int,
        cheats_used: bool,
        abandoned: bool = False,
    ) -> bool:
        """Determine whether a finished run requires name entry."""
        # Ignore duplicate endings and calls made before a game starts.
        if not self.run_active or self.run_finalized:
            return False

        self.run_active = False
        self.run_finalized = True
        self.pending_kind = None
        self.pending_score = None

        # Cheating always takes priority, including abandoned runs.
        if cheats_used:
            self.pending_kind = EntryKind.SHAME

        # Only completed legitimate runs can enter the Hall of Fame.
        elif not abandoned and self.high_scores.qualifies(score):
            self.pending_kind = EntryKind.FAME
            self.pending_score = score

        return self.pending_kind is not None

    def submit_name(self, name: str) -> bool:
        """Validate and save the pending leaderboard entry."""
        if self.pending_kind is None:
            return False

        # Normalize input before checking leaderboard-specific rules.
        normalized_name = name.strip().upper()

        if self.pending_kind == EntryKind.FAME:
            # Fame entries require exactly three ASCII capital letters.
            if (
                len(normalized_name) != 3
                or not normalized_name.isascii()
                or not normalized_name.isalpha()
                or self.pending_score is None
            ):
                return False

            self.high_scores.add_score(
                HighScoreEntry(normalized_name, self.pending_score)
            )

        else:
            # The Center of Shade accepts names up to ten characters.
            if not 1 <= len(normalized_name) <= 10:
                return False

            self.high_scores.record_cheater(
                ShameEntry(normalized_name)
            )

        # Clear the pending entry only after submission succeeds.
        self.pending_kind = None
        self.pending_score = None
        return True
