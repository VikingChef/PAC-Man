
"""Application orchestrator for Pac-Man."""

import time
from enum import Enum, auto
from random import randint
from types import TracebackType

import pygame as pg

from pacman.app.actions import CharSelectAction
from pacman.app.actions import MainMenuAction, center
from pacman.app.app_display import AppDisplay
from pacman.app.cheat_code import CheatCode
from pacman.app.cheat_panel import CheatPanel
from pacman.app.frame_presentation import render_current_frame
from pacman.app.game_renderer import render_game
from pacman.app.highscore_board import HighScoreBoard
from pacman.app.highscore_select import (
    HighScoreSelect,
    HighScoreSelectAction,
)
from pacman.app.input_handler import handle_events
from pacman.app.maze_view import (
    build_maze_layout,
    calculate_block_positions,
)
from pacman.app.menu_renderer import (
    render_character_select,
    render_highscore_select,
    render_main_menu,
    render_menu_canvas,
)
from pacman.app.name_entry import NameEntryAction, NameEntryScreen
from pacman.app.pause_menu import PauseMenu, PauseMenuAction
from pacman.app.sprite_animator import SpriteAnimator
from pacman.app.viewport import render_canvas, screen_to_canvas
from pacman.config.models import GameConfig, LevelConfig
from pacman.game.cheat_mode import CheatMode
from pacman.game.collision_rules import CollisionOutcome
from pacman.game.game_session import GameSession
from pacman.game.gameplay import GameplayUpdater
from pacman.game.highscores import HighScoreManager
from pacman.game.level import Level
from pacman.game.level_factory import create_level
from pacman.game.run_finalizer import EntryKind, RunFinalizer
from pacman.game.state import GameState
from pacman.maze.direction import Direction
from pacman.app.instructions_screen import InstructionsScreen
from pacman.app.menu_renderer import render_instructions
from pacman.app.startup_splash import StartupSplash


class AppState(Enum):
    """Possible states of the Pac-Man application."""

    MAIN_MENU = auto()
    PLAYING = auto()
    LEVEL_INTRO = auto()
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

        # Gameplay and leaderboard decisions have separate owners.
        self.session = GameSession(config)
        self.high_score_manager = HighScoreManager(
            config.highscore_filename
        )
        self.run_finalizer = RunFinalizer(self.high_score_manager)

        self.queen_chosen: CharSelectAction | None = None
        self.changing_queen = False

        # AppDisplay owns the game's visual resources.
        self.display = AppDisplay()

        self.startup_splash = StartupSplash(self.display.screen)

        # Each menu operates on its appropriate logical canvas.
        self.pause_menu = PauseMenu(self.display.game_canvas)
        self.name_entry = NameEntryScreen(self.display.menu_canvas)
        self.highscore_select = HighScoreSelect(
            self.display.menu_canvas
        )
        self.highscore_board = HighScoreBoard(
            self.display.menu_canvas
        )

        self.instructions_screen = InstructionsScreen(
            self.display.menu_canvas
        )

        # None means the two-button Hall selection screen is visible.
        self.active_highscore_board: EntryKind | None = None
        self.pause_background: pg.Surface | None = None

        # Maze geometry changes whenever a level is loaded.
        self.active_level_layout: list[list[str]] = []
        self.block_pos: list[list[tuple[int, int]]] = []

        # Keep visual movement separate from logical movement.
        self.sprite_animator = SpriteAnimator(self.display.block)

        # Timed transitions must not block the main loop.
        self.timeout_started_at: float | None = None
        self.death_started_at: float | None = None
        self.level_intro_started_at: float | None = None

        # Cheats retain their existing score-invalidation callback.
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
        """Center the background within the physical display."""
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
        """Render the remaining level time for the HUD."""
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

            # Capture state before input changes it.
            previous_state = self.state
            previous_panel_open = self.cheat_panel_open

            self._load_bg()
            self._get_events()

            # The gameplay layer manages movement and timing.
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

            # Screen presentation remains in the existing renderer.
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
        self.state = new_state

    def _finalize_run(self, abandoned: bool = False) -> bool:
        """Finalize a run and open name entry when appropriate."""
        if self.game_state is None:
            return False

        needs_name = self.run_finalizer.finish_run(
            score=self.game_state.score,
            cheats_used=self.cheat_mode.cheats_used,
            abandoned=abandoned,
        )

        if needs_name:
            # The finalizer determines which leaderboard is pending.
            kind = self.run_finalizer.pending_kind
            if kind is None:
                return False

            self.name_entry.begin(kind)
            self.cheat_panel_open = False
            self.change_state(AppState.NAME_ENTRY)

        return needs_name

    def submit_high_score_name(self, name: str) -> bool:
        """Submit a completed name and return to the main menu."""
        if not self.run_finalizer.submit_name(name):
            return False

        self.change_state(AppState.MAIN_MENU)
        return True

    def handle_name_entry_action(
        self,
        action: NameEntryAction,
    ) -> None:
        """Handle submission or abandonment of leaderboard entry."""
        if self.state != AppState.NAME_ENTRY:
            return

        if action == NameEntryAction.SUBMIT:
            # Invalid names leave the entry screen open for correction.
            self.submit_high_score_name(self.name_entry.name)

        elif action == NameEntryAction.MAIN_MENU:
            # Refusing to identify yourself earns the name ASS.
            self.submit_high_score_name("ASS")

        elif action == NameEntryAction.EXIT:
            # Escape saves the default entry before exiting.
            if self.run_finalizer.submit_name("ASS"):
                self.running = False

    def pause_game(self) -> None:
        """Pause the game during gameplay."""
        if self.state == AppState.PLAYING:
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

            if not self._finalize_run(abandoned=True):
                self.change_state(AppState.MAIN_MENU)

        elif action == PauseMenuAction.CHANGE_QUEEN:
            # Character changes must preserve the current run.
            self.changing_queen = True
            self.change_state(AppState.CHAR_SELECT)

        elif action == PauseMenuAction.QUIT_GAME:
            self.stop()

        elif action == PauseMenuAction.RESTART_LEVEL:
            if self.game_state is None:
                return

            # Restart current-level points without losing earlier ones.
            self.session.restart_level()
            level_config = self.config.levels[
                self.game_state.current_level - 1
            ]
            self._load_level(
                level_config=level_config,
                seed=randint(0, 2**31 - 1),
            )
            self.pause_background = None

    def change_queen(self, new_queen: CharSelectAction) -> None:
        """Remember the currently selected playable queen."""
        self.queen_chosen = new_queen

    def stop(self) -> None:
        """Finish a pending entry or handle an ordinary quit."""
        if self.state == AppState.NAME_ENTRY:
            # Window close during name entry defaults to ASS.
            if self.run_finalizer.submit_name("ASS"):
                self.running = False
            return

        # An ordinary quit records an abandoned cheated run.
        if self._finalize_run(abandoned=True):
            return

        self.running = False

    def _get_events(self) -> None:
        """Handle startup input or delegate ordinary application input."""
        if (
            self.state == AppState.MAIN_MENU
            and not self.startup_splash.finished(time.monotonic())
        ):
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
            return

        handle_events(self, AppState)

        handle_events(self, AppState)

    def _load_level(
        self,
        level_config: LevelConfig,
        seed: int,
    ) -> None:
        """Create and prepare a level using its configuration."""
        if self.queen_chosen is None:
            raise ValueError(
                "Cannot create a level without a selected character."
            )

        # The session owns level creation and logical state.
        level = self.session.load_level(
            level_config,
            seed,
            self.queen_chosen,
            create_level,
        )

        # Build the visual maze independently of game control.
        self.active_level_layout = build_maze_layout(level)
        self.block_pos = calculate_block_positions(
            self.active_level_layout,
            self.display.block,
        )

        # Clear movement animations from the previous level.
        self.sprite_animator.reset(self.block_pos)

        # Show the one-second level introduction.
        self.level_intro_started_at = time.monotonic()
        self.change_state(AppState.LEVEL_INTRO)

    def start_new_game(self) -> None:
        """Start a fresh run and prepare its first level."""
        self.changing_queen = False

        # New runs clear every previous cheat setting.
        self.cheat_mode = CheatMode(self._reset_score_after_cheat)

        # Reset gameplay and leaderboard finalization together.
        self.session.start_run()
        self.run_finalizer.start_run()

        first_level_config = self.config.levels[0]

        self._load_level(
            level_config=first_level_config,
            seed=self.config.seed,
        )

    def _load_bg(self) -> None:
        """Advance loading-screen background frames."""
        frame: pg.Surface | None = next(
            self.display.frame_gen,
            None,
        )

        if frame is not None:
            self.display.bg.append(frame)

            # Begin animation timing when the first frame arrives.
            if len(self.display.bg) == 1:
                self.start_time = time.time() * 1000

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
        """Coordinate player movement and application transitions."""
        level = self.active_level
        if level is None or self.game_state is None:
            return False

        result = self.session.move_player(
            direction,
            self.cheat_mode,
        )
        if not result.moved:
            return False

        # Preserve the previous cell for visual interpolation.
        if result.previous_position is not None:
            self.sprite_animator.start_player_move(
                result.previous_position,
                level.player.position,
                time.monotonic(),
            )

        # Advance only after the maze is complete.
        if result.level_complete:
            self._advance_level()

        # Resolve collisions after movement and collection.
        self.resolve_ghost_collisions()
        return True

    def resolve_ghost_collisions(self) -> None:
        """Handle the application response to ghost collisions."""
        if self.active_level is None or self.game_state is None:
            return

        if self.state != AppState.PLAYING:
            return

        outcome = self.session.check_collision(self.cheat_mode)
        if outcome != CollisionOutcome.PLAYER_CAUGHT:
            return

        # Display the collision before deducting a life.
        self.death_started_at = time.monotonic()
        self.sprite_animator.stop_player_move()

        for ghost in self.active_level.check_ghost_collision():
            self.sprite_animator.stop_ghost_move(ghost)

        self.change_state(AppState.DYING)

    def _finish_death(self) -> None:
        """Complete the death transition and update game state."""
        if self.game_state is None or self.active_level is None:
            return

        game_over = self.session.finish_death()
        self.death_started_at = None

        if game_over:
            if not self._finalize_run():
                self.change_state(AppState.GAME_OVER)
            return

        # Clear animations after the gameplay layer respawns.
        self.sprite_animator.reset()
        self.change_state(AppState.PLAYING)

    def _advance_level(self) -> None:
        """Advance to the next level or show victory."""
        if self.game_state is None:
            return

        next_level_config = self.session.advance_level()

        if next_level_config is None:
            if not self._finalize_run():
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
            if not self._finalize_run():
                self.change_state(AppState.GAME_OVER)
            return

        # Restart the current level with a fresh maze.
        self._load_level(
            level_config=current_level_config,
            seed=randint(0, 2**31 - 1),
        )

    def _handle_main_menu_action(
        self,
        action: MainMenuAction,
    ) -> None:
        """Handle actions selected from the main menu."""
        if action == MainMenuAction.START_GAME:
            self.change_state(AppState.CHAR_SELECT)

        elif action == MainMenuAction.VIEW_HIGHSCORES:
            # Always enter through the two illustrated Hall buttons.
            self.active_highscore_board = None
            self.change_state(AppState.HIGHSCORES)

        elif action == MainMenuAction.SHOW_INSTRUCTIONS:
            self.change_state(AppState.INSTRUCTIONS)

        elif action == MainMenuAction.EXIT:
            self.stop()

    def handle_highscores_event(
        self,
        event: pg.event.Event,
    ) -> None:
        """Navigate between the Hall selection and its two boards."""
        if self.state != AppState.HIGHSCORES:
            return

        # Escape goes back one screen instead of quitting the game.
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            if self.active_highscore_board is not None:
                self.active_highscore_board = None
            else:
                self.change_state(AppState.MAIN_MENU)
            return

        if self.active_highscore_board is None:
            # The selection screen reports which Hall was chosen.
            action = self.highscore_select.handle_event(event)

            if action == HighScoreSelectAction.HALL_OF_FAME:
                self.active_highscore_board = EntryKind.FAME

            elif action == HighScoreSelectAction.HALL_OF_SHAME:
                self.active_highscore_board = EntryKind.SHAME

            elif action == HighScoreSelectAction.MAIN_MENU:
                self.change_state(AppState.MAIN_MENU)

        else:
            # Both leaderboard screens use the same Back control.
            if self.highscore_board.handle_event(event):
                self.active_highscore_board = None

    def _handle_char_select_action(
        self,
        action: CharSelectAction,
    ) -> None:
        """Handle actions from character selection."""
        if action == CharSelectAction.MAIN_MENU:
            if self.changing_queen:
                # Back returns to the paused game.
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
            # Change only artwork, never the ongoing run.
            if self.active_level is None:
                return

            sprite_name = (
                "waka"
                if action == CharSelectAction.WAKA_WAKA_WANDA
                else "ms-pellet"
            )
            self.active_level.player.set_sprite(sprite_name)
            self.change_queen(action)
            self.changing_queen = False
            self.pause_background = None
            self.change_state(AppState.PLAYING)
            return

        # A selection from the main menu starts a fresh run.
        self.change_queen(action)
        self.start_new_game()

    def _run_main_menu(self) -> None:
        """Render the main menu over its animated background."""
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
        """Render the paused application state."""
        if self.pause_background is not None:
            self.display.game_canvas.blit(
                self.pause_background,
                (0, 0),
            )
        else:
            self._run_game()

        mouse_position = screen_to_canvas(
            pg.mouse.get_pos(),
            self.display.game_canvas.get_size(),
            self.display.screen.get_size(),
        )
        self.pause_menu.render_pause_menu(
            mouse_position
            if mouse_position is not None
            else (-1, -1)
        )

    def _run_game_over(self) -> None:
        """Handle the game-over application state."""
        # Game-over presentation remains a separate UI task.
        pass

    def _run_victory(self) -> None:
        """Handle the victory application state."""
        # Victory presentation remains a separate UI task.
        pass

    def _run_name_entry(self) -> None:
        """Render high-score name entry on the logical menu canvas."""
        mouse_position = screen_to_canvas(
            pg.mouse.get_pos(),
            self.display.menu_canvas.get_size(),
            self.display.screen.get_size(),
        )

        self.name_entry.render(
            mouse_position
            if mouse_position is not None
            else (-1, -1)
        )

        render_canvas(
            self.display.menu_canvas,
            self.display.screen,
        )

    def _run_highscores(self) -> None:
        """Render Hall selection or the chosen illustrated board."""
        if self.active_highscore_board is None:
            # The choice screen shares the main menu's animated backdrop.
            render_highscore_select(
                self.display.screen,
                self.display.menu_canvas,
                self.display.bg,
                self.start_time,
                self.highscore_select,
                self.display.bg_files,
            )
            return

        # Individual Hall artwork replaces the animated background.
        mouse_position = screen_to_canvas(
            pg.mouse.get_pos(),
            self.display.menu_canvas.get_size(),
            self.display.screen.get_size(),
        )

        self.highscore_board.render(
            self.active_highscore_board,
            self.high_score_manager,
            mouse_position
            if mouse_position is not None
            else (-1, -1),
        )

        render_menu_canvas(
            self.display.screen,
            self.display.menu_canvas,
        )

    def _run_instructions(self) -> None:
        """Render instructions over the animated menu background."""
        render_instructions(
            self.display.screen,
            self.display.menu_canvas,
            self.display.bg,
            self.start_time,
            self.instructions_screen,
            self.display.bg_files,
        )

    def __enter__(self) -> "PacManApp":
        """Return this application as a context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Release Pygame resources after application shutdown."""
        pg.quit()
