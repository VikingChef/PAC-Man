"""Application orchestrator for Pac-Man."""

import time
from enum import Enum, auto
from random import randint
from types import TracebackType

import pygame as pg

from pacman.app.actions import CharSelectAction
from pacman.app.actions import MainMenuAction, center
from pacman.config.models import GameConfig, LevelConfig
from pacman.game.level import Level
from pacman.game.level_factory import create_level
from pacman.game.state import GameState
from pacman.maze.direction import Direction
from pacman.game.cheat_mode import CheatMode
from pacman.app.cheat_code import CheatCode
from pacman.app.cheat_panel import CheatPanel
from pacman.app.game_renderer import (
    render_game,
)
from pacman.app.menu_renderer import (
    render_character_select,
    render_main_menu,
)
from pacman.game.gameplay import GameplayUpdater
from pacman.app.maze_view import (
    build_maze_layout,
    calculate_block_positions,
)
from pacman.app.input_handler import handle_events
from pacman.app.frame_presentation import render_current_frame
from pacman.game.collision_rules import CollisionOutcome
from pacman.game.game_session import GameSession
from pacman.app.app_display import AppDisplay
from pacman.app.sprite_animator import SpriteAnimator
from pacman.app.pause_menu import PauseMenu, PauseMenuAction
from pacman.app.viewport import screen_to_canvas


class AppState(Enum):
    """Possible states of the Pac-Man application."""

    MAIN_MENU = auto()
    PLAYING = auto()
    DYING = auto()
    PAUSED = auto()
    TIMEOUT = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    NAME_ENTRY = auto()
    HIGHSCORES = auto()
    INSTRUCTIONS = auto()
    CHAR_SELECT = auto()


class PacManApp:
    """Coordinate the main Pac-Man application flow."""

    def __init__(self, config: GameConfig) -> None:
        """Initialize the application and its shared components."""
        pg.init()

        # Application lifecycle.
        self.config = config
        self.state = AppState.MAIN_MENU
        self.running = True
        self.start_time = time.time() * 1000

        # Gameplay state is created after character selection.
        self.session = GameSession(config)
        self.queen_chosen: CharSelectAction | None = None
        # Character selection can also be opened from a paused run.
        self.changing_queen = False

        # AppDisplay creates and owns the visual resources.
        self.display = AppDisplay()
        self.pause_menu = PauseMenu(self.display.game_canvas)
        self.pause_background: pg.Surface | None = None

        # Maze geometry is rebuilt whenever the level changes.
        self.active_level_layout: list[list[str]] = []
        self.block_pos: list[list[tuple[int, int]]] = []

        # Keep visual interpolation separate from logical maze movement.
        self.sprite_animator = SpriteAnimator(self.display.block)

        # Timed transitions must not block the main loop.
        self.timeout_started_at: float | None = None
        self.death_started_at: float | None = None

        # Cheats retain their existing scoring callback.
        self.cheat_mode = CheatMode(self._reset_score_after_cheat)
        self.cheat_code = CheatCode()
        self.cheat_panel_open = False
        self.cheat_panel = CheatPanel()

        # Keyboard input maps directly to maze directions.
        self.key_map: dict[int, Direction] = {
            pg.K_UP: Direction.NORTH,
            pg.K_w: Direction.NORTH,
            pg.K_DOWN: Direction.SOUTH,
            pg.K_s: Direction.SOUTH,
            pg.K_RIGHT: Direction.EAST,
            pg.K_d: Direction.EAST,
            pg.K_LEFT: Direction.WEST,
            pg.K_a: Direction.WEST,
        }

    @property
    def game_state(self) -> GameState | None:
        """Expose the session's current run for existing callers."""
        return self.session.game_state

    @game_state.setter
    def game_state(self, value: GameState | None) -> None:
        """Allow tests and integration code to supply run state."""
        self.session.game_state = value

    @property
    def active_level(self) -> Level | None:
        """Expose the session's level to presentation and timing."""
        return self.session.active_level

    @active_level.setter
    def active_level(self, value: Level | None) -> None:
        """Allow tests and integration code to supply a level."""
        self.session.active_level = value

    @property
    def bg_pos(self) -> tuple[int, int]:
        """Center the loaded background within the physical display."""
        if self.display.bg == []:
            return (0, 0)

        bg_x: int = center(
            self.display.screen.get_width(),
            self.display.bg[0].get_width(),
        )
        bg_y: int = center(
            self.display.screen.get_height(),
            self.display.bg[0].get_height(),
        )
        return (bg_x, bg_y)

    @property
    def timer(self) -> pg.Surface | None:
        """Render the remaining level time for the HUD, if available."""
        if self.active_level is None:
            return None

        return self.display.font.render(
            str(self.active_level.remaining_time),
            True,
            color="white",
        )

    def run(self) -> None:
        """Run gameplay updates, presentation and frame timing."""
        previous_time = time.monotonic()
        gameplay = GameplayUpdater(self.active_level)

        while self.running:
            iter_start = time.time()
            current_time = time.monotonic()
            elapsed_time = current_time - previous_time
            previous_time = current_time

            # Capture state before input can change it.
            previous_state = self.state
            previous_panel_open = self.cheat_panel_open

            self._load_bg()
            self._get_events()

            # The gameplay layer manages level and ghost timing.
            timed_out = gameplay.update(
                level=self.active_level,
                game_state=self.game_state,
                cheat_mode=self.cheat_mode,
                elapsed_time=elapsed_time,
                current_time=current_time,
                was_playing=previous_state == AppState.PLAYING,
                is_playing=lambda: self.state == AppState.PLAYING,
                was_paused=previous_state == AppState.PAUSED,
                is_paused=self.state == AppState.PAUSED,
                was_panel_open=previous_panel_open,
                panel_open=self.cheat_panel_open,
                ghost_animations=self.sprite_animator.ghost_moves,
                resolve_collisions=self.resolve_ghost_collisions,
            )

            if timed_out:
                self.timeout_started_at = current_time
                self.change_state(AppState.TIMEOUT)

            # Presentation decides which screen and overlays to draw.
            render_current_frame(
                self,
                AppState,
                current_time,
            )

            pg.display.flip()

            # Preserve the existing approximate 60 FPS limit.
            iter_end = time.time()
            time.sleep(
                max(
                    0,
                    1 / 60 - (iter_end - iter_start),
                )
            )

    def change_state(self, new_state: AppState) -> None:
        """Change the current application state."""

        # Keep all application state transitions in one place.
        self.state = new_state

    def pause_game(self) -> None:
        """Pause the game during gameplay."""
        if self.state == AppState.PLAYING:
            # Retain the already-rendered frame to freeze visual movement.
            self.pause_background = self.display.game_canvas.copy()
            self.change_state(AppState.PAUSED)

    def resume_game(self) -> None:
        """Resume gameplay when the application is paused."""
        if self.state == AppState.PAUSED:
            self.pause_background = None
            self.change_state(AppState.PLAYING)

    def handle_pause_action(self, action: PauseMenuAction) -> None:
        """Apply a pause-menu selection to application state."""
        if self.state != AppState.PAUSED:
            return

        if action == PauseMenuAction.RESUME_GAME:
            self.resume_game()
        elif action == PauseMenuAction.BACK_TO_MAIN_MENU:
            self.pause_background = None
            self.change_state(AppState.MAIN_MENU)
        elif action == PauseMenuAction.CHANGE_QUEEN:
            # Keep the current run intact while the player selects artwork.
            self.changing_queen = True
            self.change_state(AppState.CHAR_SELECT)
        elif action == PauseMenuAction.QUIT_GAME:
            self.stop()
        elif action == PauseMenuAction.RESTART_LEVEL:
            if self.game_state is None:
                return
            # Rewind current-level points, retaining completed-level
            # points and the player's remaining lives.
            self.session.restart_level()
            level_config = self.config.levels[
                self.game_state.current_level - 1
            ]
            self._load_level(
                level_config=level_config,
                seed=randint(0, 2**31 - 1),
            )
            self.pause_background = None
            self.change_state(AppState.PLAYING)

    def change_queen(self, new_queen: CharSelectAction) -> None:
        self.queen_chosen = new_queen

    def stop(self) -> None:
        """Stop the Pac-Man application."""

        # End the main application loop cleanly.
        self.running = False

    def _get_events(self) -> None:
        """Delegate application input to the input handler."""
        handle_events(self, AppState)

    def _load_level(
        self,
        level_config: LevelConfig,
        seed: int,
    ) -> None:
        """Create and prepare a level using its configuration and maze seed."""

        # All game starts, level advances and retries use this single path.
        # The UI must choose a character before any level can be loaded.
        if self.queen_chosen is None:
            raise ValueError(
                'Cannot create a level without a selected character.'
            )

        # The session owns level creation and the logical level state.
        level = self.session.load_level(
            level_config,
            seed,
            self.queen_chosen,
            create_level,
        )

        # Build the visual maze independently of application control.
        self.active_level_layout = build_maze_layout(level)
        self.block_pos = calculate_block_positions(
            self.active_level_layout,
            self.display.block,
        )

        # Clear visual movement left over from the previous level.
        self.sprite_animator.reset(self.block_pos)

    def start_new_game(self) -> None:
        """Start a fresh run and prepare its first level."""
        self.changing_queen = False
        # A new run clears previous cheat settings and scoring locks.
        self.cheat_mode = CheatMode(self._reset_score_after_cheat)

        # The session owns the initial score, lives and level.
        self.session.start_run()

        first_level_config = self.config.levels[0]

        # The app prepares the Pygame level and visual maze.
        self._load_level(
            level_config=first_level_config,
            seed=self.config.seed,
        )

        self.change_state(AppState.PLAYING)

    def _load_bg(self) -> None:
        """Advance loading-screen background frames."""
        # Read the next frame from the display's background generator.
        frame: pg.Surface | None = next(
            self.display.frame_gen,
            None,
        )

        if frame is not None:
            # Store the frame with the other display resources.
            self.display.bg.append(frame)

            # Start both background and title animations when the first
            # frame arrives. Do not reset their clocks for later frames.
            if len(self.display.bg) == 1:
                self.start_time = time.time() * 1000

            # Preserve the existing loading progress calculation.
            self.display.loading.render_bar(
                min(
                    4,
                    len(self.display.bg) * 5 // self.display.bg_files,
                )
            )

    def _reset_score_after_cheat(self) -> None:
        """Invalidate the score after cheating."""
        self.session.invalidate_score()

    def award_points(self, points: int) -> None:
        """Delegate point awards to the session's scoring rules."""
        self.session.award_points(self.cheat_mode, points)

    def move_player(self, direction: Direction) -> bool:
        """Coordinate player movement and its application transitions."""
        level = self.active_level
        if level is None or self.game_state is None:
            return False

        result = self.session.move_player(direction, self.cheat_mode)
        if not result.moved:
            return False

        # Preserve the previous cell for visual interpolation.
        if result.previous_position is not None:
            self.sprite_animator.start_player_move(
                result.previous_position,
                level.player.position,
                time.monotonic(),
            )

        # Progress only after completing the current maze.
        if result.level_complete:
            self._advance_level()

        # Resolve collisions after movement and collection.
        self.resolve_ghost_collisions()
        return True

    def resolve_ghost_collisions(self) -> None:
        """Handle the application response to ghost collisions."""
        if self.active_level is None or self.game_state is None:
            return

        # Collisions cannot interrupt an existing death transition.
        if self.state != AppState.PLAYING:
            return

        outcome = self.session.check_collision(self.cheat_mode)

        if outcome != CollisionOutcome.PLAYER_CAUGHT:
            return

        # The gameplay rules identified a fatal collision.
        # Display it before deducting the player's life.
        self.death_started_at = time.monotonic()

        # Stop interpolating the colliding characters so their
        # sprites meet at their shared logical position.
        self.sprite_animator.stop_player_move()

        for ghost in self.active_level.check_ghost_collision():
            self.sprite_animator.stop_ghost_move(ghost)

        self.change_state(AppState.DYING)

    def _finish_death(self) -> None:
        """Complete the death transition and update the screen state."""
        if self.game_state is None or self.active_level is None:
            return

        game_over = self.session.finish_death()

        self.death_started_at = None

        if game_over:
            self.change_state(AppState.GAME_OVER)
            return

        # Clear animations after the gameplay layer has respawned
        # the player and ghosts.
        self.sprite_animator.reset()

        self.change_state(AppState.PLAYING)

    def _advance_level(self) -> None:
        """Advance to the next level or show victory."""
        if self.game_state is None:
            return

        next_level_config = self.session.advance_level()

        if next_level_config is None:
            self.change_state(AppState.VICTORY)
            return

        # Preserve the existing random seed behaviour.
        next_level_seed = randint(0, 2**31 - 1)

        self._load_level(
            level_config=next_level_config,
            seed=next_level_seed,
        )

    def _finish_timeout(self) -> None:
        """Restart an expired level or end the game."""
        if self.game_state is None:
            return

        self.timeout_started_at = None

        current_level_config = self.session.resolve_timeout()

        if current_level_config is None:
            self.change_state(AppState.GAME_OVER)
            return

        # Restart the same level with a fresh random maze seed.
        self._load_level(
            level_config=current_level_config,
            seed=randint(0, 2**31 - 1),
        )

        self.change_state(AppState.PLAYING)

    def _handle_main_menu_action(
        self,
        action: MainMenuAction,
    ) -> None:
        """Handle an action selected from the main menu."""

        # Translate UI choices into application behaviour.
        if action == MainMenuAction.START_GAME:
            self.change_state(AppState.CHAR_SELECT)
        elif action == MainMenuAction.VIEW_HIGHSCORES:
            self.change_state(AppState.HIGHSCORES)
        elif action == MainMenuAction.SHOW_INSTRUCTIONS:
            self.change_state(AppState.INSTRUCTIONS)
        elif action == MainMenuAction.EXIT:
            self.stop()

    def _handle_char_select_action(
        self,
        action: CharSelectAction,
    ) -> None:
        """Handle events coming from the Character Selection Menu.
        Args:
            action (CharSelectAction): Action (clicks) in character
                                       selection menu.
        """
        if action == CharSelectAction.MAIN_MENU:
            if self.changing_queen:
                # Back returns to the paused run, not the main menu.
                self.changing_queen = False
                self.change_state(AppState.PAUSED)
            else:
                self.change_state(AppState.MAIN_MENU)
            return

        if action not in (
            CharSelectAction.WAKA_WAKA_WANDA,
            CharSelectAction.MS_POWER_PELLET,
        ):
            return

        if self.changing_queen:
            # Only change the live player's artwork. Never reload its maze,
            # regenerate collectibles or reset the run's score and timers.
            if self.active_level is None:
                return
            sprite_name = (
                "waka" if action == CharSelectAction.WAKA_WAKA_WANDA
                else "ms-pellet"
            )
            self.active_level.player.set_sprite(sprite_name)
            self.change_queen(action)
            self.changing_queen = False
            self.pause_background = None
            self.change_state(AppState.PLAYING)
            return

        # Choosing a character from the main menu still starts a new run.
        self.change_queen(action)
        self.start_new_game()

    def _run_main_menu(self) -> None:
        """Render the main menu over a fullscreen animated background."""
        # Delegate background, hover coordinates and menu scaling.
        render_main_menu(
            self.display.screen,
            self.display.menu_canvas,
            self.display.bg,
            self.start_time,
            self.display.main_menu,
            self.display.bg_files,
        )

    def _run_char_select(self) -> None:
        """Render character selection over the animated background."""
        # Use the same presentation pipeline as the main menu.
        render_character_select(
            self.display.screen,
            self.display.menu_canvas,
            self.display.bg,
            self.start_time,
            self.display.char_select,
            self.display.bg_files,
        )

    def _run_game(self) -> None:
        """Render the current game using the dedicated renderer."""
        if self.active_level is None:
            return

        # The application supplies the current gameplay and visual state.
        # The renderer owns how those elements appear on the canvas.
        render_game(
            canvas=self.display.game_canvas,
            level=self.active_level,
            game_state=self.game_state,
            cheat_mode=self.cheat_mode,
            wall_sprite=self.display.block,
            maze_layout=self.active_level_layout,
            block_positions=self.block_pos,
            sprite_position=self.sprite_animator.position,
            sprite_animator=self.sprite_animator,
            hud=self.display.hud,
            disco_effects=self.display.disco_effects,
        )

    def _run_pause_menu(self) -> None:
        """Handle the paused application state."""

        # The frozen frame prevents animations advancing behind the menu.
        if self.pause_background is not None:
            self.display.game_canvas.blit(self.pause_background, (0, 0))
        else:
            self._run_game()

        # Hover coordinates must match the scaled gameplay canvas.
        mouse_position = screen_to_canvas(
            pg.mouse.get_pos(),
            self.display.game_canvas.get_size(),
            self.display.screen.get_size(),
        )
        self.pause_menu.render_pause_menu(
            mouse_position if mouse_position is not None else (-1, -1)
        )

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

    def __enter__(self) -> "PacManApp":
        """Dunder method for context managers.
        Returns:
            PacManApp: PacManApp object
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Dunder method for context managers.
        Args:
            exc_type (type[BaseException] | None): Class of the exception
                raised inside the ``with`` block, or None if it exited
                normally.
            exc (BaseException | None): The exception instance, or None.
            tb (TracebackType | None): Traceback of the exception, or None.
        """
        pg.quit()
