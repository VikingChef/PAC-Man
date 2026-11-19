
"""Coordinate gameplay updates independently of rendering."""

from collections.abc import Callable

from pacman.game.cheat_mode import CheatMode
from pacman.game.ghost import Ghost, GhostState
from pacman.game.level import Level
from pacman.game.state import GameState


CellPosition = tuple[int, int]
GhostAnimations = dict[Ghost, tuple[CellPosition, float]]


class GameplayUpdater:
    """Manage gameplay timing, ghost movement and collisions."""

    def __init__(self, level: Level | None) -> None:
        """Initialise the timing state for the active level."""
        self.previous_level = level
        self.accumulated_time = 0.0
        self.ghost_accumulated_time = 0.0

    def update(
        self,
        level: Level | None,
        game_state: GameState | None,
        cheat_mode: CheatMode,
        elapsed_time: float,
        current_time: float,
        was_playing: bool,
        is_playing: Callable[[], bool],
        was_paused: bool,
        is_paused: bool,
        was_panel_open: bool,
        panel_open: bool,
        ghost_animations: GhostAnimations,
        resolve_collisions: Callable[[], None],
    ) -> bool:
        """Advance gameplay and report whether the level timed out."""
        # Never carry unfinished time into a newly created level.
        level_changed = level is not self.previous_level

        if level_changed:
            self.accumulated_time = 0.0
            self.ghost_accumulated_time = 0.0
            self.previous_level = level

        playing_now = is_playing()

        # Gameplay advances only during uninterrupted active play.
        # Opening or closing the cheat panel skips the transition frame.
        gameplay_active = (
            was_playing
            and playing_now
            and not was_panel_open
            and not panel_open
            and not level_changed
            and level is not None
            and game_state is not None
        )

        if not gameplay_active:
            # Ordinary pauses and cheat-panel pauses preserve
            # accumulated fractions without counting paused time.
            preserve_time = (
                panel_open
                or was_panel_open
                or is_paused
                or (was_paused and playing_now)
            )

            if not preserve_time:
                self.accumulated_time = 0.0
                self.ghost_accumulated_time = 0.0

            return False

        # The active-play checks establish that these objects exist.
        if level is None or game_state is None:
            return False

        self.accumulated_time += elapsed_time

        # Level time advances in complete seconds.
        while self.accumulated_time >= 1.0:
            level.tick(
                1,
                freeze_level_timer=cheat_mode.timer_stopped,
            )
            self.accumulated_time -= 1.0

            # Let the application handle the TIMEOUT state.
            if level.is_time_up:
                return True

        # Ghost movement has its own configurable interval.
        self.ghost_accumulated_time += elapsed_time
        ghost_interval = (
            level.config.ghost_move_interval_ms / 1000
        )

        while (
            is_playing()
            and self.ghost_accumulated_time >= ghost_interval
        ):
            if not cheat_mode.ghosts_frozen:
                previous_positions = {
                    ghost: ghost.position
                    for ghost in level.ghosts
                }

                level.move_ghosts()

                # Record visual transitions without drawing anything.
                for ghost in level.ghosts:
                    if (
                        ghost.state != GhostState.EATEN
                        and ghost.position != previous_positions[ghost]
                    ):
                        ghost_animations[ghost] = (
                            previous_positions[ghost],
                            current_time,
                        )

            self.ghost_accumulated_time -= ghost_interval

            # Collision checks still run when ghosts are frozen.
            lives_before_collision = game_state.lives
            resolve_collisions()

            # Stop processing if the player dies or gameplay ends.
            if (
                not is_playing()
                or game_state.lives < lives_before_collision
            ):
                self.ghost_accumulated_time = 0.0
                break

        return False
