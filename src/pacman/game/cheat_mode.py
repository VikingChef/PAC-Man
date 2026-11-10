"""Manage cheat settings for Pac-Man gameplay."""


class CheatMode:
    """Manage gameplay cheat settings."""

    def __init__(self) -> None:
        """Initialize cheat mode."""

        self.invincible = False
        self.ghosts_frozen = False
        self.disco_enabled = False
        self.timer_stopped = False
        self.cheats_used = False
        self.being_fabulous = False

    def toggle_invincibility(self) -> None:
        """Toggle invincibility on or off."""
        self.invincible = not self.invincible

        if self.invincible:
            self.cheats_used = True

    def toggle_ghost_freeze(self) -> None:
        """Toggle freezing of ghost movement."""

        self.ghosts_frozen = not self.ghosts_frozen

        if self.ghosts_frozen:
            self.cheats_used = True

    def toggle_disco_enabled(self) -> None:
        """Toggle disco mode."""

        self.disco_enabled = not self.disco_enabled
        self.being_fabulous = self.disco_enabled

    def toggle_timer_stopped(self) -> None:
        """Toggle the timer freeze on or off."""

        self.timer_stopped = not self.timer_stopped

        if self.timer_stopped:
            self.cheats_used = True
