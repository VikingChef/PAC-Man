
"""Manage cheat settings for Pac-Man gameplay."""

from collections.abc import Callable


class CheatMode:
    """Manage gameplay cheat settings and cheating history."""

    def __init__(
        self,
        on_first_cheat: Callable[[], None] | None = None,
    ) -> None:
        """Initialize cheat mode and its optional notification."""
        self.invincible = False
        self.ghosts_frozen = False
        self.disco_enabled = False
        self.timer_stopped = False
        self.cheats_used = False
        self.being_fabulous = False

        # Notify the application when cheating first becomes permanent.
        # CheatMode does not need to know how scores are stored.
        self.on_first_cheat = on_first_cheat

    def _mark_cheated(self) -> None:
        """Record cheating and notify the application once."""
        # Cheating remains recorded even after every cheat is disabled.
        if self.cheats_used:
            return

        self.cheats_used = True

        # The application decides what happens to the player's score.
        if self.on_first_cheat is not None:
            self.on_first_cheat()

    def toggle_invincibility(self) -> None:
        """Toggle invincibility on or off."""
        self.invincible = not self.invincible

        if self.invincible:
            self._mark_cheated()

    def toggle_ghost_freeze(self) -> None:
        """Toggle freezing of ghost movement."""
        self.ghosts_frozen = not self.ghosts_frozen

        if self.ghosts_frozen:
            self._mark_cheated()

    def toggle_disco_enabled(self) -> None:
        """Toggle disco mode."""
        self.disco_enabled = not self.disco_enabled
        self.being_fabulous = self.disco_enabled

    def toggle_timer_stopped(self) -> None:
        """Toggle the timer freeze on or off."""
        self.timer_stopped = not self.timer_stopped

        if self.timer_stopped:
            self._mark_cheated()
