"""Application orchestrator for Pac-Man."""

from enum import Enum, auto

from src.pacman.app.actions import MainMenuAction, MainMenu, CharacterSelect
from src.pacman.app.actions import LoadingBar, center
from src.pacman.config.models import GameConfig
from src.pacman.game.state import GameState
from types import TracebackType
import pygame as pg
import os
from collections.abc import Iterator
import time


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

        # Track start time for animations
        self.start_time: float = time.time() * 1000

        # Create run-specific game state only when a new game starts.
        self.game_state: GameState | None = None
        self.screen: pg.Surface = pg.display.set_mode(
            flags=pg.FULLSCREEN
        )

        # Background
        path: str = './src/pacman/app/images/bg-frames'
        self.bg_files: int = len(os.listdir(path))
        self.frame_gen: Iterator[pg.Surface] = load_frames(path)
        self.bg: list[pg.Surface] = []

        self.main_menu: MainMenu = MainMenu(self.screen)
        self.char_select: CharacterSelect = CharacterSelect(self.screen)
        self.loading: LoadingBar = LoadingBar(self.screen)

    @property
    def bg_pos(self) -> tuple[int, int]:
        if self.bg == []:
            return (0, 0)
        else:
            bg_x: int = center(
                self.screen.get_width(),
                self.bg[0].get_width(),
            )
            bg_y: int = center(
                self.screen.get_height(),
                self.bg[0].get_height(),
            )
            return (bg_x, bg_y)

    def run(self) -> None:
        """Run the Pac-Man application."""

        # Keep one central loop and route each cycle by application state.
        while self.running:
            iter_start: float = time.time()

            self._load_bg()
            self._get_events()

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

    def start_new_game(self) -> None:
        """Create the state for a new Pac-Man game."""

        # Build a fresh run from the validated configuration.
        self.game_state = GameState(
            score=0,
            lives=self.config.lives,
            current_level=1,
        )

        # Move into gameplay once the new run is ready.
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
                        len(self.bg) * 5 // self.bg_files,
                    )
                )

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
            self.bg_pos,
        )
        self.main_menu.render_main_menu(
            self.start_time,
            mouse,
            self.screen
            )

    def _run_char_select(self) -> None:
        """Handle the character select application state."""

        pass

    def _run_game(self) -> None:
        """Handle the active gameplay application state."""

        # Gameplay systems will be coordinated from here.
        pass

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

    def __enter__(self) -> 'PacManApp':
        """Dunder method for context managers.

        Returns:
            Visualizer: Visualizer object
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None
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
            x[x.find('_') + 1:x.find('.')]
        ),
    )

    for frame in dir_list:
        yield pg.image.load(
            f'{path}/{frame}'
        ).convert()
