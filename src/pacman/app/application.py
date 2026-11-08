"""Application orchestrator for Pac-Man."""
import os
import time
from collections.abc import Iterator
from enum import Enum, auto
from random import randint
from types import TracebackType
import pygame as pg
from pacman.app.actions import CharacterSelect, CharSelectAction
from pacman.app.actions import LoadingBar, MainMenu, MainMenuAction, center
from pacman.app.actions import load_trans_image, IMAGES
from pacman.config.models import GameConfig
from pacman.game.ghost import GhostState
from pacman.game.level import Level
from pacman.game.level_factory import create_level
from pacman.game.pacgum import PacgumType
from pacman.game.state import GameState
from pacman.maze.direction import Direction
from pacman.maze.wall import Wall


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
    CHAR_SELECT = auto()


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
        # Track start time for animations.
        self.start_time: float = time.time() * 1000
        # Create run-specific game state only when a new game starts.
        self.game_state: GameState | None = None
        # Create the active level only when a new game starts.
        self.active_level: Level | None = None
        self.screen: pg.Surface = pg.display.set_mode(
            flags=pg.FULLSCREEN
        )
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
        self.waka: pg.Surface = load_trans_image(f'{IMAGES}/waka-sprite.png')
        self.ms_pellet: pg.Surface = load_trans_image(
            f'{IMAGES}/ms-pellet-sprite.png'
        )
        # Visual movement is independent of the logical maze coordinates.
        self.visual_move_start: tuple[int, int] | None = None
        self.visual_move_end: tuple[int, int] | None = None
        self.visual_move_started: float = 0.0
        self.visual_move_duration: float = 0.12

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
        """Run the Pac-Man application."""

        # Track real elapsed time between frames.
        previous_time: float = time.monotonic()
        accumulated_time: float = 0.0
        ghost_accumulated_time: float = 0.0
        previous_level: Level | None = self.active_level

        # Keep one central loop and route each cycle by application state.
        while self.running:
            iter_start: float = time.time()

            # Measure elapsed time using a monotonic clock.
            current_time: float = time.monotonic()
            elapsed_time = current_time - previous_time
            previous_time = current_time

            # Remember the state before processing new input.
            previous_state = self.state
            self._load_bg()
            self._get_events()

            # Detect level change and lose the previous level's partial time.
            level_changed = self.active_level is not previous_level
            if level_changed:
                accumulated_time = 0.0
                ghost_accumulated_time = 0.0
                previous_level = self.active_level

            # Advance timers only during uninterrupted active gameplay.
            if (
                previous_state == AppState.PLAYING
                and self.state == AppState.PLAYING
                and not level_changed
                and self.active_level is not None
                and self.game_state is not None
            ):
                accumulated_time += elapsed_time

                # Process complete seconds while preserving fractions.
                while accumulated_time >= 1.0:
                    self.active_level.tick(1)
                    accumulated_time -= 1.0

                # Accumulate time independently for ghost movement.
                ghost_accumulated_time += elapsed_time

                # Convert the configured movement interval to seconds.
                ghost_interval = (
                    self.active_level.config.ghost_move_interval_ms / 1000
                )

                # Move ghosts once for each completed movement interval.
                while ghost_accumulated_time >= ghost_interval:
                    self.active_level.move_ghosts()
                    ghost_accumulated_time -= ghost_interval

                    # Resolve collisions caused by ghost movement.
                    lives_before_collision = self.game_state.lives
                    self.resolve_ghost_collisions()

                    # Stop processing movements after death or game ends.
                    if (
                        self.state != AppState.PLAYING
                        or self.game_state.lives < lives_before_collision
                    ):
                        ghost_accumulated_time = 0.0
                        break

            elif (
                self.state == AppState.PAUSED
                or (
                    previous_state == AppState.PAUSED
                    and self.state == AppState.PLAYING
                )
            ):
                # Preserve partial seconds while paused or resuming.
                pass
            else:
                # Reset both timers when leaving gameplay.
                accumulated_time = 0.0
                ghost_accumulated_time = 0.0
            if self.state == AppState.MAIN_MENU:
                self._run_main_menu()
            elif self.state == AppState.CHAR_SELECT:
                self._run_char_select()
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
            pg.display.flip()
            # Limit the application to approximately 60 FPS.
            iter_end: float = time.time()
            time.sleep(
                max(
                    0,
                    1 / 60 - (iter_end - iter_start)
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
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.stop()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.stop()
            if self.state == AppState.MAIN_MENU:
                menu_state: MainMenuAction | None = (
                    self.main_menu.handle_event(event)
                )
                if menu_state is not None:
                    self._handle_main_menu_action(menu_state)
            elif self.state == AppState.CHAR_SELECT:
                char_state: CharSelectAction | None = (
                    self.char_select.handle_event(event)
                )
                if char_state is not None:
                    self._handle_char_select_action(char_state)
            elif self.state == AppState.PLAYING and event.type == pg.KEYDOWN:
                # Route keyboard input through the tested maze-aware movement.
                if event.key == pg.K_UP:
                    self.move_player(Direction.NORTH)
                elif event.key == pg.K_DOWN:
                    self.move_player(Direction.SOUTH)
                elif event.key == pg.K_LEFT:
                    self.move_player(Direction.WEST)
                elif event.key == pg.K_RIGHT:
                    self.move_player(Direction.EAST)

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
        self.active_level_layout = self._get_active_level_layout()
        self.block_pos = self._get_block_pos()
        self.visual_move_start = None
        self.visual_move_end = None
        # Move into gameplay once the new run and level are ready.
        self.change_state(AppState.PLAYING)

    def _load_bg(self) -> None:
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

    def move_player(self, direction: Direction) -> bool:
        """Move the active player in the requested direction."""
        # Gameplay movement requires both an active level and run-wide state.
        if self.active_level is None or self.game_state is None:
            return False

        # Delegate movement to the Player and stop if the maze blocks the move.
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
            self.game_state.score += self.config.points_per_pacgum
        elif collected_pacgum == PacgumType.SUPER_PACGUM:
            self.game_state.score += self.config.points_per_super_pacgum
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
            self.game_state.lives -= 1
            if self.game_state.lives == 0:
                self.change_state(AppState.GAME_OVER)
            else:
                self.active_level.reset_positions()
                self.visual_move_start = None
                self.visual_move_end = None
            return

        # Eat frightened ghosts and award points for each successful capture.
        for ghost in colliding_ghosts:
            if ghost.eat():
                self.game_state.score += self.config.points_per_ghost

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
            pacgum_count=self.config.pacgum
        )
        # Refresh rendering coordinates for the newly generated maze.
        self.active_level_layout = self._get_active_level_layout()
        self.block_pos = self._get_block_pos()
        self.visual_move_start = None
        self.visual_move_end = None

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
        """Handle the active gameplay application state."""
        if self.active_level is None:
            return

        # Draw the current maze, then the selected player sprite.
        self.screen.fill(color="black")
        for i, row in enumerate(self.active_level_layout):
            for j, col in enumerate(row):
                if col == 'wall':
                    self.screen.blit(self.block, self.block_pos[i][j])
        # Map logical maze cells onto the expanded visual grid.
        player_x, player_y = self.active_level.player.position
        target = self.block_pos[player_y * 2 + 1][player_x * 2 + 1]
        draw_x, draw_y = target

        if (
            self.visual_move_start is not None
            and self.visual_move_end == self.active_level.player.position
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

        if self.queen_chosen == CharSelectAction.WAKA_WAKA_WANDA:
            self.screen.blit(self.waka, (draw_x, draw_y))
        elif self.queen_chosen == CharSelectAction.MS_POWER_PELLET:
            self.screen.blit(self.ms_pellet, (draw_x, draw_y))

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
