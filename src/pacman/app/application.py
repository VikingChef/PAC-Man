"""Application orchestrator for Pac-Man."""

from enum import Enum, auto
from random import randint

from pacman.app.actions import MainMenuAction
from pacman.config.models import GameConfig
from pacman.game.level import Level
from pacman.game.level_factory import create_level
from pacman.game.pacgum import PacgumType
from pacman.game.state import GameState
from pacman.maze.direction import Direction


class AppState(Enum):
    """Possible states of the Pac-Man application."""

    # Define the screens and modes controlled by the orchestrator.
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    NAME_ENTRY = auto()
    HIGHSCORES = auto()
    INSTRUCTIONS = auto()


class PacManApp:
    """Coordinate the main Pac-Man application flow."""

    def __init__(self, config: GameConfig) -> None:
        """Create the application with validated configuration data."""

        # Store the validated configuration for the whole application.
        self.config = config

        # Start the application in the main menu.
        self.state = AppState.MAIN_MENU

        # Track whether the main application loop should continue.
        self.running = True

        # Create run-specific game state only when a new game starts.
        self.game_state: GameState | None = None

        # Create the active level only when a new game starts.
        self.active_level: Level | None = None

    def run(self) -> None:
        """Run the Pac-Man application."""

        # Keep one central loop and route each cycle by application state.
        while self.running:
            if self.state == AppState.MAIN_MENU:
                self._run_main_menu()
            elif self.state == AppState.PLAYING:
                self._run_game()
            elif self.state == AppState.PAUSED:
                self._run_pause_menu()
            elif self.state == AppState.GAME_OVER:
                self._run_game_over()
            elif self.state == AppState.VICTORY:
                self._run_victory()
            elif self.state == AppState.NAME_ENTRY:
                self._run_name_entry()
            elif self.state == AppState.HIGHSCORES:
                self._run_highscores()
            elif self.state == AppState.INSTRUCTIONS:
                self._run_instructions()

    def change_state(self, new_state: AppState) -> None:
        """Change the current application state."""

        # Keep all application state transitions in one place.
        self.state = new_state

    def stop(self) -> None:
        """Stop the Pac-Man application."""

        # End the main application loop cleanly.
        self.running = False

    def start_new_game(self) -> None:
        """Create the state for a new Pac-Man game."""

        # Build fresh run-wide state from the validated configuration.
        self.game_state = GameState(
            score=0,
            lives=self.config.lives,
            current_level=1,
        )

        # Build the first playable level and its active game state.
        first_level_config = self.config.levels[0]
        self.active_level = create_level(
            config=first_level_config,
            seed=self.config.seed,
            time_limit=self.config.level_max_time,
            pacgum_count=self.config.pacgum,
        )

        # Move into gameplay once the new run and level are ready.
        self.change_state(AppState.PLAYING)

    def move_player(self, direction: Direction) -> bool:
        """Move the active player in the requested direction."""

        # Gameplay movement requires both an active level and run-wide state.
        if self.active_level is None or self.game_state is None:
            return False

        # Delegate movement to the Player and stop if the maze blocks the move.
        moved = self.active_level.player.move(
            self.active_level.maze,
            direction,
        )

        if not moved:
            return False

        # Check the player's new position and remove any pacgum found there.
        collected_pacgum = self.active_level.collect_pacgum(
            self.active_level.player.position,
        )

        # Apply the configured score for the collected pacgum type.
        if collected_pacgum == PacgumType.PACGUM:
            self.game_state.score += self.config.points_per_pacgum

        elif collected_pacgum == PacgumType.SUPER_PACGUM:
            self.game_state.score += self.config.points_per_super_pacgum

        # Advance once collecting the final pacgum completes the level.
        if self.active_level.is_complete:
            self._advance_level()

        # Preserve the movement contract: a successful move returns True.
        return True

    def _advance_level(
        self,
    ) -> None:
        """Advance the player to the next level."""

        # Level progression requires an active run-wide game state.
        if self.game_state is None:
            return

        # Completing the final configured level ends the run in victory.
        if self.game_state.current_level >= len(self.config.levels):
            self.change_state(AppState.VICTORY)
            return

        # Advance the run-wide level number before selecting its configuration.
        self.game_state.current_level += 1

        # Convert the one-based level number to the zero-based config index.
        next_level_config = self.config.levels[
            self.game_state.current_level - 1
        ]

        # Later levels use a fresh random seed instead of the fixed first seed.
        next_level_seed = randint(0, 2**31 - 1)

        # Replace the current level while preserving run-wide score and lives.
        self.active_level = create_level(
            config=next_level_config,
            seed=next_level_seed,
            time_limit=self.config.level_max_time,
            pacgum_count=self.config.pacgum,
        )

    def _handle_main_menu_action(
        self,
        action: MainMenuAction,
    ) -> None:
        """Handle an action selected from the main menu."""

        # Translate UI choices into application behaviour.
        if action == MainMenuAction.START_GAME:
            self.start_new_game()
        elif action == MainMenuAction.VIEW_HIGHSCORES:
            self.change_state(AppState.HIGHSCORES)
        elif action == MainMenuAction.SHOW_INSTRUCTIONS:
            self.change_state(AppState.INSTRUCTIONS)
        elif action == MainMenuAction.EXIT:
            self.stop()

    def _run_main_menu(self) -> None:
        """Handle the main menu application state."""

        # Main menu input and presentation will connect here.
        pass

    def _run_game(self) -> None:
        """Handle the active gameplay application state."""

        # Gameplay systems will be coordinated from here.
        if self.game_state is None or self.active_level is None:
            return

    def _run_pause_menu(self) -> None:
        """Handle the paused application state."""

        # Pause menu input and presentation will connect here.
        pass

    def _run_game_over(self) -> None:
        """Handle the game-over application state."""

        # Game-over presentation and transition will connect here.
        pass

    def _run_victory(self) -> None:
        """Handle the victory application state."""

        # Victory presentation and transition will connect here.
        pass

    def _run_name_entry(self) -> None:
        """Handle highscore name entry."""

        # Highscore name input will connect to the UI layer here.
        pass

    def _run_highscores(self) -> None:
        """Handle the highscore application state."""

        # Highscore presentation will connect to the UI layer here.
        pass

    def _run_instructions(self) -> None:
        """Handle the instructions application state."""

        # Instruction presentation will connect to the UI layer here.
        pass
