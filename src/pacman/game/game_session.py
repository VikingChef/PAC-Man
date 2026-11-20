"""Own an active run, level transitions and gameplay outcomes."""

from collections.abc import Callable

from pacman.app.actions import CharSelectAction
from pacman.config.models import GameConfig, LevelConfig
from pacman.game import run_lifecycle, scoring
from pacman.game.cheat_mode import CheatMode
from pacman.game.collision_rules import (
    CollisionOutcome,
    lose_life,
    resolve_collision,
)
from pacman.game.level import Level
from pacman.game.pacgum import PacgumType
from pacman.game.player_actions import PlayerMoveResult, move_and_collect
from pacman.game.state import GameState
from pacman.maze.direction import Direction


class GameSession:
    """Own the logical run and its active level."""

    def __init__(self, config: GameConfig) -> None:
        """Keep the configuration and start without a playable run."""
        self.config = config
        self.game_state: GameState | None = None
        self.active_level: Level | None = None
        self.level_start_score = 0
        self.mercy_used = False
        self.current_level_seed: int | None = None

    def start_run(self) -> None:
        """Begin a fresh run with the configured score and lives."""
        self.game_state = run_lifecycle.create_run(self.config)
        self.active_level = None
        self.level_start_score = 0
        self.mercy_used = False

    def restart_level(self) -> None:
        """Discard points earned since the current level began."""
        if self.game_state is not None:
            # A retry must never recover points invalidated by cheating.
            self.game_state.score = self.level_start_score

    def request_mercy(self) -> bool:
        """Grant one three-life pardon after the run ends."""
        if self.game_state is None:
            return False

        # Mercy is available only once, after the final life is lost.
        if self.mercy_used or self.game_state.lives > 0:
            return False

        # Preserve completed-level points, not repeated collectibles.
        self.restart_level()

        self.game_state.lives = 3
        self.mercy_used = True
        return True

    def load_level(
        self,
        level_config: LevelConfig,
        seed: int,
        queen: CharSelectAction,
        factory: Callable[..., Level],
    ) -> Level:
        """Create and retain the next playable level."""
        # Inject the factory so application-level tests can control it.
        level = factory(
            config=level_config,
            seed=seed,
            time_limit=self.config.level_max_time,
            pacgum_count=self.config.pacgum,
            player_sprite=queen,
        )
        # Retain the seed so mercy can recreate the same maze.
        self.current_level_seed = seed
        self.active_level = level
        return level

    def award_points(self, cheat_mode: CheatMode, points: int) -> None:
        """Apply score rules to this run."""
        scoring.award_points(self.game_state, cheat_mode, points)

    def invalidate_score(self) -> None:
        """Invalidate the score after a cheat is activated."""
        scoring.invalidate_score(self.game_state)
        # Never restore an invalidated score through a level restart.
        self.level_start_score = 0

    def move_player(
        self,
        direction: Direction,
        cheat_mode: CheatMode,
    ) -> PlayerMoveResult:
        """Move the player and award points for collected pacgum."""
        if self.active_level is None or self.game_state is None:
            return PlayerMoveResult(moved=False)

        result = move_and_collect(self.active_level, direction)
        if not result.moved:
            return result

        # Keep collectible scoring in the game session, not the app.
        if result.collected_pacgum == PacgumType.PACGUM:
            self.award_points(cheat_mode, self.config.points_per_pacgum)
        elif result.collected_pacgum == PacgumType.SUPER_PACGUM:
            self.award_points(
                cheat_mode,
                self.config.points_per_super_pacgum,
            )
        return result

    def check_collision(self, cheat_mode: CheatMode) -> CollisionOutcome:
        """Resolve logical ghost contact and its scoring effects."""
        if self.active_level is None or self.game_state is None:
            return CollisionOutcome.NONE
        return resolve_collision(
            self.active_level,
            self.game_state,
            cheat_mode,
            self.config.points_per_ghost,
        )

    def finish_death(self) -> bool:
        """Complete life loss and report whether the run has ended."""
        if self.active_level is None or self.game_state is None:
            return False
        return lose_life(self.active_level, self.game_state)

    def advance_level(self) -> LevelConfig | None:
        """Return the next level or None when the run is complete."""
        if self.game_state is None:
            return None
        next_level = run_lifecycle.advance_level(
            self.game_state, self.config
        )
        if next_level is not None:
            # Completed levels are permanent; only current-level points
            # should disappear if the player chooses to restart.
            self.level_start_score = self.game_state.score
        return next_level

    def resolve_timeout(self) -> LevelConfig | None:
        """Deduct a life and return the level to retry if alive."""
        if self.game_state is None:
            return None
        return run_lifecycle.resolve_timeout(self.game_state, self.config)
