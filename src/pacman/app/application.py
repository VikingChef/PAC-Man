"""Application orchestrator for Pac-Man."""

import os
import time
from collections.abc import Iterator
from typing import Final
from enum import Enum, auto
from random import randint
from types import TracebackType

import pygame as pg

from pacman.app.actions import CharacterSelect, CharSelectAction
from pacman.app.actions import LoadingBar, MainMenu, MainMenuAction, center
from pacman.app.actions import load_trans_image, IMAGES
from pacman.config.models import GameConfig, LevelConfig
from pacman.game.ghost import GhostState, Ghost
from pacman.game.level import Level
from pacman.game.level_factory import create_level
from pacman.game.pacgum import PacgumType
from pacman.game.state import GameState
from pacman.maze.direction import Direction
from pacman.maze.wall import Wall
from pacman.game.cheat_mode import CheatMode
from pacman.app.cheat_code import CheatCode
from pacman.app.cheat_panel import CheatPanel
from pacman.app.disco_effects import DiscoEffects


ALL_WALLS: Final = Wall.WEST | Wall.EAST | Wall.SOUTH | Wall.NORTH


class AppState(Enum):
    """Possible states of the Pac-Man application."""

    # Define the screens and modes controlled by the orchestrator.
    MAIN_MENU = auto()
    PLAYING = auto()
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
        """Create the application with validated configuration data."""

        # Initialise Pygame before creating the display or loading sprites.
        pg.init()

        # Store the validated configuration for the whole application.
        self.config = config

        # Start the application in the main menu.
        self.state = AppState.MAIN_MENU

        # Track whether the main application loop should continue.
        self.running = True

        # Track start time for animations.
        self.start_time: float = time.time() * 1000

        # Create run-specific game state only when a new game starts.
        self.game_state: GameState | None = None

        # Create the active level only when a new game starts.
        self.active_level: Level | None = None
        self.screen: pg.Surface = pg.display.set_mode(
            flags=pg.FULLSCREEN
        )

        # Start of the three-second timeout display, if one is active.
        self.timeout_started_at: float | None = None

        # Background.
        path: str = "./src/pacman/app/images/bg-frames"
        self.bg_files: int = len(os.listdir(path))
        self.frame_gen: Iterator[pg.Surface] = load_frames(path)
        self.bg: list[pg.Surface] = []
        self.main_menu: MainMenu = MainMenu(self.screen)
        self.char_select: CharacterSelect = CharacterSelect(self.screen)
        self.loading: LoadingBar = LoadingBar(self.screen)
        self.queen_chosen: CharSelectAction | None = None
        self.active_level_layout: list[list[str]] = []
        self.block: pg.Surface = load_trans_image(f'{IMAGES}/level-block.gif')
        self.block_pos: list[list[tuple[int, int]]] = []

        # Visual movement is independent of the logical maze coordinates.
        self.visual_move_start: tuple[int, int] | None = None
        self.visual_move_end: tuple[int, int] | None = None
        self.visual_move_started: float = 0.0
        self.visual_move_duration: float = 0.12

        # Track each ghost's movement independently of its logical position.
        # Each entry stores the starting cell and animation start time.
        self.ghost_visual_moves: dict[
            Ghost, tuple[tuple[int, int], float]
        ] = {}

        # CheatMode owns the actual gameplay settings and cheat history.
        self.cheat_mode = CheatMode()

        # Recognise the secret sequence independently of the game controls.
        self.cheat_code = CheatCode()

        # The application controls panel visibility and gameplay suspension.
        self.cheat_panel_open = False

        # UI components do not own cheat settings. They receive the active
        # CheatMode when needed, avoiding stale state after a new game.
        self.cheat_panel = CheatPanel()

        # Decorative disco effects remain independent of gameplay logic.
        self.disco_effects = DiscoEffects()

        # Keep keyboard bindings together so arrows and WASD behave alike.
        self.key_map: dict[int, Direction] = {
            pg.K_UP: Direction.NORTH,
            pg.K_w: Direction.NORTH,
            pg.K_DOWN: Direction.SOUTH,
            pg.K_s: Direction.SOUTH,
            pg.K_RIGHT: Direction.EAST,
            pg.K_d: Direction.EAST,
            pg.K_LEFT: Direction.WEST,
            pg.K_a: Direction.WEST
        }

        # HUD resources introduced by the UI branch.
        self.font: pg.font.Font = pg.font.Font(
            "src/pacman/app/assets/PressStart2P-Regular.ttf", 40)
        self.level_bg: pg.Surface = load_trans_image(f'{IMAGES}/level-bg.png')

    @property
    def bg_pos(self) -> tuple[int, int]:
        if self.bg == []:
            return (0, 0)
        bg_x: int = center(
            self.screen.get_width(),
            self.bg[0].get_width(),
        )
        bg_y: int = center(
            self.screen.get_height(),
            self.bg[0].get_height(),
        )
        return (bg_x, bg_y)

    @property
    def timer(self) -> pg.Surface | None:
        """Render the remaining level time for the HUD, if available."""
        if self.active_level is None:
            return None
        return self.font.render(
            str(self.active_level.remaining_time),
            True,
            color='white'
            )

    def _get_active_level_layout(self) -> list[list[str]]:
        if self.active_level is None:
            return []
        width: int = self.active_level.maze.width
        height: int = self.active_level.maze.height
        maze_lst: list = [self.interchange_list_element(
            list(row),
            'wall',
            width
            ) for row in self.active_level.maze.maze_grid]
        output: list = self.interchange_list_element(
            maze_lst,
            ['wall'],
            height
            )
        output = self.create_paths(output, width)
        return output

    def _get_block_pos(self) -> list[list[tuple[int, int]]]:
        output: list[list[tuple[int, int]]] = []
        if self.active_level is not None:
            for i, row in enumerate(self.active_level_layout):
                output.append([])
                for j, col in enumerate(row):
                    x: int = int(
                        (self.screen.get_width()
                         - self.block.get_width()
                         * len(self.active_level_layout[0])) / 2
                        + j * self.block.get_width()
                    )
                    y: int = int(
                        (self.screen.get_height()
                         - self.block.get_height()
                         * len(self.active_level_layout)) / 2
                        + i * self.block.get_height()
                    )
                    output[i].append((x, y))
        return output

    def create_paths(
        self, output: list[list[str]], width: int
    ) -> list[list[str]]:
        """Draw maze passages using the same rules as player movement."""
        if self.active_level is None:
            return output
        maze = self.active_level.maze
        for i, row in enumerate(output):
            if i % 2 == 0:
                output[i] = ['wall'] * (width * 2 + 1)
        for i, row in enumerate(output):
            for j, cell in enumerate(row):
                if type(cell) is not Wall:
                    continue
                position = ((j - 1) // 2, (i - 1) // 2)
                if position in maze.reserved_positions:
                    output[i][j] = 'wall'
                    continue
                output[i][j] = 'path'
                if maze.can_move(position, Direction.EAST):
                    output[i][j + 1] = 'path'
                if maze.can_move(position, Direction.SOUTH):
                    output[i + 1][j] = 'path'
        return output

    def interchange_list_element(
        self, src_lst: list, element: str | list, size: int
    ) -> list:
        """Put elements inbetween of other list elements.
        Args:
            src_lst (list): the original list
            element (str | list): the element to but inbetween
            size (int): how big the list is
        Returns:
            list: the transformed list
        """
        output: list = []
        i: int = 0
        for row in range(size * 2):
            if row % 2 == 0:
                output.append(element)
            else:
                output.append(src_lst[i])
                i += 1
        output.append(element)
        return output

    def run(self) -> None:
        """Run the application and coordinate gameplay updates.

        The main loop processes input, advances gameplay timers,
        moves ghosts and renders the current application screen.

        Opening the Fabulous Control Panel temporarily suspends
        gameplay without changing the normal application state.

        Both ordinary pauses and panel pauses preserve fractional
        timer progress while excluding time spent paused.
        """

        # Track elapsed time independently for level timers and ghosts.
        previous_time: float = time.monotonic()
        accumulated_time: float = 0.0
        ghost_accumulated_time: float = 0.0

        # Remember the active level to detect transitions.
        previous_level: Level | None = self.active_level

        while self.running:
            iter_start: float = time.time()

            # Use a monotonic clock so changes to the system clock
            # cannot unexpectedly affect gameplay.
            current_time: float = time.monotonic()
            elapsed_time = current_time - previous_time
            previous_time = current_time

            # Remember both states before processing input.
            # This lets us recognise the frames when a pause begins
            # or ends, rather than accidentally counting those frames.
            previous_state = self.state
            previous_panel_open = self.cheat_panel_open

            self._load_bg()
            self._get_events()

            # A new level must never inherit unfinished timer
            # fractions or pending ghost movements from the old one.
            level_changed = self.active_level is not previous_level

            if level_changed:
                accumulated_time = 0.0
                ghost_accumulated_time = 0.0
                previous_level = self.active_level

            # Gameplay may advance only when the application was
            # playing both before and after event processing.
            #
            # Opening, displaying or closing the control panel
            # suspends ALL gameplay updates, including ghost
            # movement, frightened timers and respawn timers.
            gameplay_active = (
                previous_state == AppState.PLAYING
                and self.state == AppState.PLAYING
                and not previous_panel_open
                and not self.cheat_panel_open
                and not level_changed
                and self.active_level is not None
                and self.game_state is not None
            )

            if (
                gameplay_active
                and self.active_level is not None
                and self.game_state is not None
            ):
                # Accumulate gameplay seconds without losing fractions.
                accumulated_time += elapsed_time

                while accumulated_time >= 1.0:
                    self.active_level.tick(
                        1,
                        freeze_level_timer=self.cheat_mode.timer_stopped,
                    )
                    accumulated_time -= 1.0

                    # A timeout stops further gameplay updates.
                    if self.active_level.is_time_up:
                        self.timeout_started_at = current_time
                        self.change_state(AppState.TIMEOUT)
                        break

                # Ghost movement has its own independent interval.
                ghost_accumulated_time += elapsed_time

                ghost_interval = (
                    self.active_level.config.ghost_move_interval_ms
                    / 1000
                )

                while (
                    self.state == AppState.PLAYING
                    and ghost_accumulated_time >= ghost_interval
                ):
                    if not self.cheat_mode.ghosts_frozen:
                        # Remember logical positions before movement.
                        # Rendering uses these to interpolate sprites.
                        previous_positions = {
                            ghost: ghost.position
                            for ghost in self.active_level.ghosts
                        }

                        self.active_level.move_ghosts()

                        # Record only ghosts that actually moved.
                        # Eaten ghosts teleport and must not slide.
                        for ghost in self.active_level.ghosts:
                            if (
                                ghost.state != GhostState.EATEN
                                and ghost.position
                                != previous_positions[ghost]
                            ):
                                self.ghost_visual_moves[ghost] = (
                                    previous_positions[ghost],
                                    current_time,
                                )

                    ghost_accumulated_time -= ghost_interval

                    # Resolve collisions even when ghost movement
                    # is frozen, preserving existing game behaviour.
                    lives_before_collision = self.game_state.lives
                    self.resolve_ghost_collisions()

                    # Do not process additional ghost movements
                    # after Pac-Man loses a life or gameplay ends.
                    if (
                        self.state != AppState.PLAYING
                        or self.game_state.lives < lives_before_collision
                    ):
                        ghost_accumulated_time = 0.0
                        break

            elif (
                self.cheat_panel_open
                or previous_panel_open
                or self.state == AppState.PAUSED
                or (
                    previous_state == AppState.PAUSED
                    and self.state == AppState.PLAYING
                )
            ):
                # Preserve the partial seconds accumulated before
                # pausing, without adding elapsed wall-clock time.
                #
                # This also excludes the transition frames when
                # the control panel opens or closes.
                pass

            else:
                # Leaving active gameplay invalidates pending timer
                # fractions and ghost movement intervals.
                accumulated_time = 0.0
                ghost_accumulated_time = 0.0

            # Render the current application screen.
            #
            # Gameplay rendering, including decorative disco effects,
            # belongs in _run_game(), not in this orchestrator.
            if self.state == AppState.MAIN_MENU:
                self._run_main_menu()

            elif self.state == AppState.CHAR_SELECT:
                self._run_char_select()

            elif self.state == AppState.PLAYING:
                self._run_game()

            elif self.state == AppState.PAUSED:
                self._run_pause_menu()

            elif self.state == AppState.TIMEOUT:
                # Keep the level visible for the existing
                # three-second timeout sequence.
                if (
                    self.timeout_started_at is not None
                    and current_time - self.timeout_started_at >= 3.0
                ):
                    self._finish_timeout()
                else:
                    self._run_game()

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

            # The panel is an overlay, not another AppState.
            # Draw it after the game so its controls stay visible.
            #
            # CheatPanel receives the current CheatMode instance
            # and never owns a second copy of the cheat settings.
            if (
                self.cheat_panel_open
                and self.state == AppState.PLAYING
            ):
                self.cheat_panel.render(
                    self.screen,
                    self.cheat_mode,
                )

            pg.display.flip()

            # Limit the application to approximately 60 FPS.
            iter_end: float = time.time()
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
            self.change_state(AppState.PAUSED)

    def resume_game(self) -> None:
        """Resume gameplay when the application is paused."""
        if self.state == AppState.PAUSED:
            self.change_state(AppState.PLAYING)

    def change_queen(self, new_queen: CharSelectAction) -> None:
        self.queen_chosen = new_queen

    def stop(self) -> None:
        """Stop the Pac-Man application."""

        # End the main application loop cleanly.
        self.running = False

    def _get_events(self) -> None:
        """Dispatch Pygame events to the active application interface.

        The cheat panel takes priority over ordinary gameplay input while
        it is open. The application retains ownership of panel visibility,
        while CheatPanel handles its own mouse controls.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.stop()
                continue

            # When the panel is open, prevent input from reaching the game.
            # This also prevents mouse clicks from affecting other screens.
            if self.cheat_panel_open:
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.cheat_panel_open = False
                    self.cheat_code.reset()

                elif self.cheat_panel.handle_event(
                    event,
                    self.screen,
                    self.cheat_mode,
                ):
                    self.cheat_panel_open = False
                    self.cheat_code.reset()

                continue

            # Preserve the application's existing Escape behaviour when
            # the cheat panel is not open.
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.stop()
                continue

            if self.state == AppState.MAIN_MENU:
                menu_action: MainMenuAction | None = (
                    self.main_menu.handle_event(event)
                )

                if menu_action is not None:
                    self._handle_main_menu_action(menu_action)

            elif self.state == AppState.CHAR_SELECT:
                character_action: CharSelectAction | None = (
                    self.char_select.handle_event(event)
                )

                if character_action is not None:
                    self._handle_char_select_action(character_action)

            elif self.state == AppState.PLAYING:
                if event.type != pg.KEYDOWN:
                    continue

                # Observe gameplay keys for the secret unlock sequence.
                # The detector manages its own sequence and timing.
                unlocked = self.cheat_code.register_key(
                    event.key,
                    time.monotonic(),
                )

                if unlocked:
                    self.cheat_panel_open = True
                    continue

                # Arrow keys must still move Pac-Man while entering the
                # sequence. Cheat detection does not consume movement keys.
                if event.key in self.key_map:
                    self.move_player(self.key_map[event.key])

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

        # Pass the selected character to the shared level factory.
        self.active_level = create_level(
            config=level_config,
            seed=seed,
            time_limit=self.config.level_max_time,
            pacgum_count=self.config.pacgum,
            player_sprite=self.queen_chosen,
        )

        # Rebuild the visual maze layout and screen coordinates.
        self.active_level_layout = self._get_active_level_layout()
        self.block_pos = self._get_block_pos()

        # Clear any animation left over from the previous level.
        self.visual_move_start = None
        self.visual_move_end = None
        self.ghost_visual_moves.clear()

    def start_new_game(self) -> None:
        """Create the state for a new Pac-Man game."""

        # Reset cheat settings for the new run.
        self.cheat_mode = CheatMode()

        # Build fresh run-wide state from the validated configuration.
        self.game_state = GameState(
            score=0,
            lives=self.config.lives,
            current_level=1,
        )

        # Build the first playable level and its active game state.
        first_level_config = self.config.levels[0]
        self._load_level(
            level_config=first_level_config,
            seed=self.config.seed,
        )

        # Move into gameplay once the new run and level are ready.
        self.change_state(AppState.PLAYING)

    def _load_bg(self) -> None:
        """Advance loading-screen background frames."""
        frame: pg.Surface | None = next(
            self.frame_gen,
            None
        )
        if frame is not None:
            self.bg.append(frame)
            self.loading.render_bar(
                min(
                    4,
                    len(self.bg) * 5 // self.bg_files
                )
            )

    def award_points(self, points: int) -> None:
        """Award points, doubling them when disco mode is active."""
        if self.game_state is None:
            return

        multiplier = 2 if self.cheat_mode.disco_enabled else 1
        self.game_state.score += points * multiplier

    def move_player(self, direction: Direction) -> bool:
        """Move the active player in the requested direction."""

        # Gameplay movement requires both an active level and run-wide state.
        if self.active_level is None or self.game_state is None:
            return False

        # Delegate movement to Player; stop if the maze blocks the move.
        level = self.active_level
        previous_position = level.player.position
        moved = level.player.move(
            self.active_level.maze,
            direction
        )
        if not moved:
            return False

        # Animate between cells without changing the logical position.
        self.visual_move_start = previous_position
        self.visual_move_end = level.player.position
        self.visual_move_started = time.monotonic()

        # Check the player's new position and remove any pacgum found there.
        collected_pacgum = self.active_level.collect_pacgum(
            self.active_level.player.position
        )

        # Apply the configured score for the collected pacgum type.
        if collected_pacgum == PacgumType.PACGUM:
            self.award_points(self.config.points_per_pacgum)
        elif collected_pacgum == PacgumType.SUPER_PACGUM:
            self.award_points(self.config.points_per_super_pacgum)
            self.active_level.frighten_ghosts()

        # Advance once collecting the final pacgum completes the level.
        if self.active_level.is_complete:
            self._advance_level()

        # Resolve collisions after collecting any pacgum.
        lives_before_collision = self.game_state.lives
        self.resolve_ghost_collisions()

        # Do not advance the level after losing a life.
        if (
            self.state != AppState.PLAYING
            or self.game_state.lives < lives_before_collision
        ):
            return True

        # Preserve the movement contract: a successful move returns True.
        return True

    def resolve_ghost_collisions(self) -> None:
        """Apply the consequences of ghosts colliding with the player."""

        # Collision handling requires an active level and game state.
        if self.active_level is None or self.game_state is None:
            return

        # Nothing to resolve if no ghost shares the player's position.
        colliding_ghosts = self.active_level.check_ghost_collision()
        if not colliding_ghosts:
            return

        # An enraged ghost takes priority over frightened ghosts.
        if any(
            ghost.state == GhostState.ENRAGED
            for ghost in colliding_ghosts
        ):

            # Ignore enraged collisions while invincible.
            if self.cheat_mode.invincible:
                return
            self.game_state.lives -= 1
            if self.game_state.lives == 0:
                self.change_state(AppState.GAME_OVER)
            else:
                self.active_level.reset_positions()

                # Everyone has teleported to spawn after losing a life.
                # Discard animations from their previous positions.
                self.visual_move_start = None
                self.visual_move_end = None
                self.ghost_visual_moves.clear()
            return

        # Eat frightened ghosts and award points for each successful capture.
        for ghost in colliding_ghosts:
            if ghost.eat():
                self.award_points(self.config.points_per_ghost)

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
        self._load_level(
            level_config=next_level_config,
            seed=next_level_seed,

        )

    def _finish_timeout(self) -> None:
        """Resolve timeout and restart the level or end the game."""
        if self.game_state is None:
            return
        self.timeout_started_at = None
        self.game_state.lives -= 1
        if self.game_state.lives == 0:
            self.change_state(AppState.GAME_OVER)
            return
        current_level_config = self.config.levels[
            self.game_state.current_level - 1
        ]
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
        if action == CharSelectAction.WAKA_WAKA_WANDA:
            self.change_queen(CharSelectAction.WAKA_WAKA_WANDA)
            self.start_new_game()
        elif action == CharSelectAction.MS_POWER_PELLET:
            self.change_queen(CharSelectAction.MS_POWER_PELLET)
            self.start_new_game()
        elif action == CharSelectAction.MAIN_MENU:
            self.change_state(AppState.MAIN_MENU)

    def _run_main_menu(self) -> None:
        """Handle the main menu application state."""

        # Main menu input and presentation will connect here.
        mouse: tuple[int, int] = pg.mouse.get_pos()
        now: float = time.time() * 1000
        bg_frame: int = (
            int(now - self.start_time) // 100
        ) % len(self.bg)
        self.screen.blit(
            self.bg[bg_frame],
            self.bg_pos
        )
        self.main_menu.render_main_menu(
            self.start_time,
            mouse,
            self.screen
        )

    def _run_char_select(self) -> None:
        """Handle the character select application state."""
        mouse: tuple[int, int] = pg.mouse.get_pos()
        now: float = time.time() * 1000
        bg_frame: int = (
            int(now - self.start_time) // 100
        ) % len(self.bg)
        self.screen.blit(
            self.bg[bg_frame],
            self.bg_pos
        )
        self.char_select.render_char_select(
            mouse,
            self.screen
        )

    def _run_game(self) -> None:
        """Render the active Pac-Man level and its visual effects."""
        if self.active_level is None:
            return

        # Draw the current maze background and walls.
        self.screen.blit(self.level_bg, self.bg_pos)

        for i, row in enumerate(self.active_level_layout):
            for j, col in enumerate(row):
                if col == 'wall':
                    self.screen.blit(
                        self.block,
                        self.block_pos[i][j],
                    )

        # Fabulous Mode decorates the existing maze with rainbow lights
        # and four fixed disco balls outside its corners.
        #
        # Draw these effects before characters and collectibles so
        # the lighting cannot obscure important gameplay elements.
        if self.cheat_mode.disco_enabled and self.block_pos:
            # The outermost cells define the complete visual maze.
            # Include the final block's dimensions in the bounds.
            maze_left, maze_top = self.block_pos[0][0]
            last_x, last_y = self.block_pos[-1][-1]

            maze_bounds = pg.Rect(
                maze_left,
                maze_top,
                last_x + self.block.get_width() - maze_left,
                last_y + self.block.get_height() - maze_top,
            )

            # Decorative animation uses real time rather than
            # gameplay timers. It therefore cannot affect the
            # level countdown, ghosts or collision calculations.
            self.disco_effects.render(
                self.screen,
                maze_bounds,
                time.monotonic(),
            )

        # Each direction maps to the character-specific sprite
        # chosen in the character-selection interface.
        direction: Direction = self.active_level.player.direction
        queen: pg.Surface = (
            self.active_level.player.sprite_path[direction]
        )

        dim: tuple[int, int] = (
            queen.get_width(),
            queen.get_height(),
        )

        self.screen.blit(
            queen,
            self.pos(self.active_level.player.position, dim),
        )

        # Draw ghosts independently of Pac-Man's movement animation.
        for ghost in self.active_level.ghosts:

            # Eaten ghosts return directly to spawn without sliding.
            if ghost.state == GhostState.EATEN:
                self.ghost_visual_moves.pop(ghost, None)

                # Blink while waiting to respawn.
                if int(time.monotonic() * 4) % 2 == 0:
                    continue

            direction = ghost.direction
            sprite = ghost.sprite[direction]
            dim = (sprite.get_width(), sprite.get_height())

            # Find the screen position of the ghost's current maze cell.
            x, y = ghost.position
            target_x, target_y = self.block_pos[
                y * 2 + 1
            ][x * 2 + 1]

            draw_x, draw_y = target_x, target_y

            animation = self.ghost_visual_moves.get(ghost)

            if animation is not None:
                start_position, started_at = animation

                duration = (
                    self.active_level.config.ghost_move_interval_ms
                    / 1000
                )

                # Calculate how far through the movement animation
                # we are, keeping visual and logical positions separate.
                progress = min(
                    1.0,
                    (time.monotonic() - started_at)
                    / max(duration, 0.001),
                )

                start_x, start_y = start_position

                origin_x, origin_y = self.block_pos[
                    start_y * 2 + 1
                ][start_x * 2 + 1]

                draw_x = round(
                    origin_x + (target_x - origin_x) * progress
                )
                draw_y = round(
                    origin_y + (target_y - origin_y) * progress
                )

                # Finished animations no longer need to be stored.
                if progress >= 1.0:
                    self.ghost_visual_moves.pop(ghost, None)

            # Centre the sprite inside the visual maze cell.
            block_width = self.block.get_width()
            block_height = self.block.get_height()

            self.screen.blit(
                sprite,
                (
                    draw_x + center(block_width, dim[0]),
                    draw_y + center(block_height, dim[1]),
                ),
            )

        # The timer can be absent outside a loaded level.
        timer_surface = self.timer

        if timer_surface is not None:
            x = (
                self.screen.get_width()
                - timer_surface.get_width()
                - 10
            )

            self.screen.blit(timer_surface, (x, 10))

        # UI branch stores (pacgum type, surface) per logical cell.
        # Collectibles are drawn after disco lighting to remain visible.
        for position, pacgum in self.active_level.pacgums.items():
            dim = (
                pacgum[1].get_width(),
                pacgum[1].get_height(),
            )

            self.screen.blit(
                pacgum[1],
                self.pos(position, dim),
            )

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

    def pos(self,
            pos: tuple[int, int],
            dim: tuple[int, int]) -> tuple[int, int]:
        """Center a sprite in a maze cell, interpolating player movement."""

        # Map logical maze cells onto the expanded visual grid.
        x, y = pos
        target = self.block_pos[y * 2 + 1][x * 2 + 1]
        draw_x, draw_y = target
        if (
            self.visual_move_start is not None
            and self.visual_move_end == pos
        ):
            start_x, start_y = self.visual_move_start
            origin = self.block_pos[start_y * 2 + 1][start_x * 2 + 1]
            progress = min(
                1.0,
                (time.monotonic() - self.visual_move_started)
                / self.visual_move_duration,
            )
            draw_x = round(origin[0] + (target[0] - origin[0]) * progress)
            draw_y = round(origin[1] + (target[1] - origin[1]) * progress)
            if progress >= 1.0:
                self.visual_move_start = None
                self.visual_move_end = None
        block_x, block_y = self.block.get_width(), self.block.get_height()
        return (center(block_x, dim[0]) + draw_x,
                center(block_y, dim[1]) + draw_y)

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


def load_frames(path: str) -> Iterator[pg.Surface]:
    dir_list: list[str] = sorted(
        os.listdir(path),
        key=lambda x: int(
            x[x.find("_") + 1:x.find(".")]
        )
    )
    for frame in dir_list:
        yield pg.image.load(
            f"{path}/{frame}"
        ).convert()
