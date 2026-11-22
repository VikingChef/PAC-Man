*This project has been created as part of the 42 curriculum by ikolokou, rrasmuss.*

# Pac-Ma'am

**Two queens. Four ghosts. An unreasonable amount of pink.**

## Description

Pac-Man has been running around mazes eating dots and avoiding ghosts since 1980. We decided the formula was sound, but the wardrobe needed work.

**Pac-Ma'am** is our Python take on the arcade classic, starring **two playable drag queens: Brunhilda and Ms Power Pellet**. They share top billing. Choose your queen, tackle a maze, collect the pacgums, and try not to have your evening ruined by four exceptionally persistent ghosts.

The game keeps the core Pac-Man rules—walls, corridors, lives, ghosts, super-pacgums, scoring and level progression—but puts them inside our own rather theatrical presentation. There's character selection, a pink arcade-style interface, animated artwork, a highscore system, and a cheat panel that occasionally forgets we're supposed to be taking this seriously.

Beneath the glitter, this is a 42 Berlin software-engineering project. We built it in Python using object-oriented design, an external maze generator, configuration files, separated game and interface logic, and automated tests. It started as a manageable assignment. Then we had ideas. This is usually how these things happen.

### Meet the queens

**Brunhilda** is a bearded Viking drag queen with a winged headpiece, spectacular confidence and very little interest in being subtle.

**Ms Power Pellet** brings her own style, attitude and equally rightful claim to the spotlight. She is not Brunhilda's sidekick. They're both playable protagonists; the choice is yours.

The characters change the presentation, not the fundamental maze rules. No one should win simply because their outfit is better. That would be an entirely different game.

## Instructions

### Requirements

- Python **3.10 or newer**.
- [`uv`](https://docs.astral.sh/uv/) for dependency management.
- A graphical desktop environment capable of running Pygame.

The assigned **A-Maze-ing** package is included as a local wheel under `packages/` and installed as a project dependency. We use that package without modifying its maze-generation implementation.

From the repository root:

```bash
make install
```

Start the game using the required command-line interface:

```bash
python3 pac-man.py config.json
```

If you're using the project-managed environment rather than an independently configured Python environment, use:

```bash
PYTHONPATH=src uv run python pac-man.py config.json
```

Or simply:

```bash
make run
```

`pac-man.py` expects **exactly one argument**: a JSON configuration file. The file can have a different name. The important part is passing the path to it.

### Playing

Start from the main menu, choose Brunhilda or Ms Power Pellet, and enter the maze. Move through corridors, collect pacgums and avoid ghosts. Super-pacgums briefly turn the tables and make the ghosts edible. Clear the level to continue; finish the configured levels to win.

The game includes menus for instructions and highscores, plus in-game pause and cheat controls. The exact key bindings are displayed in the game's **Instructions** screen; that is the reference for the current build.

### Development commands

```bash
make lint              # flake8 and mypy
uv run pytest -q       # automated tests
make debug             # run under pdb
make clean             # remove development caches
```

The repository's `Makefile` defines `install`, `run`, `debug`, `clean` and `lint`. We run the tests as well as the linters because code being perfectly formatted does not make it correct. Annoying, but true.

### Packaged version

The 42 subject also requires a free, unlisted/private playable build on a public gaming platform, together with a reproducible packaging script or specification in the repository root. Packaging and the hosted build should be checked as part of the final release, not assumed to be complete because the source version runs.

## Configuration

The game reads JSON, with an extra allowance for lines beginning with `#`. Those lines are stripped before the JSON is parsed. Unknown or invalid values are handled by the loader, with warnings and safe defaults where appropriate.

The supplied `config.json` uses these settings:

| Key | Supplied value | What it controls |
| --- | --- | --- |
| `highscore_filename` | `highscores.json` | Persistent leaderboard file |
| `lives` | `3` | Starting lives |
| `pacgum` | `42` | Requested number of ordinary pacgums |
| `points_per_pacgum` | `10` | Points for an ordinary pacgum |
| `points_per_super_pacgum` | `50` | Points for a super-pacgum |
| `points_per_ghost` | `200` | Points for an edible ghost |
| `seed` | `42` | Initial maze seed |
| `level_max_time` | `90` | Per-level time limit, in seconds |
| `levels` | Ten entries, each `15 × 15` | Level count and maze sizes in the supplied file |

Each level entry specifies `number`, `width` and `height`. The loader can also accept a `ghost_move_interval_ms` setting for a level, allowing ghost movement timing to vary.

**A small but important distinction:** if the `levels` list is missing or invalid, the archived loader creates **ten fallback 21×21 levels**. That isn't the same as the ten 15×15 levels explicitly listed in the supplied configuration. We mention both because configuration handling should not be a guessing game.

For example, the configuration file can contain:

```json
{
  "lives": 3,
  "pacgum": 42,
  "seed": 42,
  "level_max_time": 90,
  "levels": [
    {"number": 1, "width": 15, "height": 15}
  ]
}
```

This is a **minimal example**, not the complete ten-level release configuration; omitted values use the loader's defaults. The full supplied file is the proper starting point for a complete playthrough.

The configuration is intentionally editable. Bad values should produce understandable messages or fallbacks rather than a spectacular Python traceback.

## Highscore

We wanted the highscore screen to feel like an old arcade machine, so we chose **three-letter initials** rather than long player names. The leaderboard keeps the **top ten** scores and saves them to a JSON file so they survive between runs.

A score must qualify for the table before it can be entered. The board starts with a set of deliberately cheeky placeholder initials; those entries are there to give the arcade some personality and a score to beat.

We also split the honours into two categories:

- **Hall of Fame:** legitimate runs, with the final score recorded against the player's initials.
- **Hall of Shame:** runs involving cheats, which get their own record instead of quietly joining the legitimate leaderboard.

The distinction matters because the cheat panel exists to make testing easier, not to let someone freeze the ghosts and declare themselves an arcade god.

Highscore loading and saving live in `src/pacman/game/highscores.py`. The run-completion logic lives separately in `src/pacman/game/run_finalizer.py`, so the rules about which score belongs where aren't buried in the drawing code. The storage code also handles malformed save data and aims not to overwrite a damaged existing file blindly.

The subject allows names of up to ten alphanumeric characters with spaces; our **three-letter A–Z initials** are a deliberate, stricter arcade-style choice.

## Maze Generation

We're required to use another team's **A-Maze-ing** maze generator rather than write our own. That's exactly what the game is structured to do.

The integration has two layers:

1. `src/pacman/game/level_factory.py` asks the supplied `MazeGenerator` for a maze, with `perfect=False` as required for Pac-Man-style corridors.
2. `src/pacman/maze/adapter.py` converts the generator's wall representation into our own `Maze` and `Wall` types, while preserving reserved cells.

This separation was worth the effort. The generator is responsible for generating mazes. Our game is responsible for interpreting them, finding a playable area, placing the player, ghosts and pacgums, and enforcing gameplay rules.

The initial level uses the configured seed, making it reproducible. Later levels use their own seeds. That lets us reproduce a problematic maze when debugging without making the entire game one eternal déjà vu.

We do **not** alter the assigned generator package. Our code adapts to its output, not the other way around.

## Implementation

We split the game into smaller pieces because having one enormous file responsible for every ghost, button, score and existential crisis became less appealing as the project grew.

The important moving parts are:

- **Game state and rules:** player movement, ghost behaviour, collisions, scoring, pacgums, lives and level progression.
- **Level creation:** generation, maze conversion, reachable play areas, spawning and placement.
- **Application flow:** moving between the main menu, character selection, gameplay, pause, game over, victory and highscores.
- **Rendering and UI:** sprites, HUD, buttons, animations, character artwork and menus.
- **Configuration and persistence:** validated settings and saved leaderboards.
- **Cheat controls:** testing aids, kept separate from legitimate scoring.

Our priority was to keep game rules out of presentation code where possible. A ghost doesn't need to know what colour the menu is. The menu doesn't need to calculate the path to a pacgum.

### Graphics Challenges: doing a lot with a little

The subject allows MiniLibX or a graphical library with equivalent capabilities. We use **Pygame**, and we paid particular attention to how the visual effects map to MiniLibX's basic image and pixel operations.

For several effects, we replaced Pygame conveniences with explicit image-buffer calculations. That includes scaling, fading and the Game Over greyscale transition. The greyscale effect was especially educational: generating the correct grey image was not the same thing as drawing it correctly over the live gameplay canvas. The solution was to write the computed pixel colours directly into the destination buffer before drawing the colourful funeral panel on top. Glamour, apparently, requires some fairly unglamorous debugging.

Other operations remain in place because their results can be described in terms of simple pixel calculations:

**Rectangles and hovering buttons.** `pygame.draw.rect()` fills or outlines areas in the pause menu, cheat controls and other interfaces. With MiniLibX, we could create an image (`mlx_new_image()`), access its pixel buffer (`mlx_get_data_addr()`), and colour the pixels inside a rectangle—or just along its edges. Hover states are similarly straightforward: detect whether the mouse is inside the button's area, then draw its highlighted image or calculate brighter colours. The pause menu and hovering buttons provide visible demonstrations.

**Additive blending (`BLEND_RGB_ADD`).** To brighten an image, add an amount to the red, green and blue numbers for each pixel, never going above 255. A pixel `(100, 50, 150)` brightened by 30 becomes `(130, 80, 180)`. MiniLibX can achieve the same result by reading, calculating and writing pixel colours.

**Multiplicative blending (`BLEND_RGBA_MULT`).** To apply a mask, multiply each colour component by the corresponding component of a second image, scaled to a 0–255 range. White leaves the colour alone, black removes it, and grey reduces it. This is how we can describe limiting disco reflections to their intended shape. Transparency can also be calculated by combining foreground and background colours in the appropriate proportions.

The overall method is the same: create an image, read its pixels, do the arithmetic, and display the result with `mlx_put_image_to_window()`.

These descriptions explain **how the same visual results can be produced with MiniLibX pixel operations**. They are the technical reasoning behind our graphics choices, not a claim that MiniLibX contains functions with the exact same names or automatic blending behaviour. We kept the existing additive and multiplicative blending calls under that interpretation.

In short, the disco is mathematics. The wigs are optional; the maths isn't.

## General Software Architecture

The source lives under `src/pacman/`, divided by responsibility:

```text
src/pacman/
├── app/        # Application state, menus, rendering, input, UI
├── config/     # Configuration models and validation
├── game/       # Gameplay, levels, ghosts, scoring and highscores
└── maze/       # Maze representation and generator adapter
```

At the top sits `PacManApp`, which coordinates the game lifecycle and screens. It uses the configuration loader to create a game session and delegates gameplay to classes and functions under `game/`. The maze adapter keeps the external generator's data format away from the rest of the game. Rendering modules under `app/` turn state into something the player can see and interact with.

Some particularly useful starting points for reading the code:

| File | Responsibility |
| --- | --- |
| `pac-man.py` | Command-line entry point |
| `src/pacman/app/application.py` | Main application and state coordination |
| `src/pacman/game/game_session.py` | Active game session |
| `src/pacman/game/level_factory.py` | Build playable levels |
| `src/pacman/maze/adapter.py` | Integrate A-Maze-ing output |
| `src/pacman/config/loader.py` | Read and validate configuration |
| `src/pacman/game/highscores.py` | Persist leaderboard data |
| `src/pacman/game/run_finalizer.py` | Decide what happens to a completed run |

We refactored when it solved an actual problem, rather than splitting files simply to produce more files. The aim was code we could explain, test and change without summoning an entirely new category of bugs.

## Testing

Our test suite uses **pytest**, alongside **flake8** and **mypy** for style and type checking.

```bash
uv run pytest -q
make lint
```

The tests cover individual game rules and application behaviour; manual playtesting remains important for things automated tests aren't very good at judging, such as whether a button is visible, a fade looks right, or a drag queen has accidentally acquired a large black rectangle for a face.

We test the game through normal play as well as the cheat controls, which help us reach otherwise time-consuming situations. Before release we also need to verify the complete ten-level journey, malformed configuration handling, score persistence, package installation and the hosted build. A passing test count alone isn't a substitute for those checks.

## Project Management

There are two of us. We needed enough organisation to divide work, make decisions and avoid stepping on each other's changes; we did not need to establish a steering committee for four ghosts.

We used Git branches, divided programming and visual/UI tasks, tracked what was done and what still needed attention, and kept notes about important technical decisions and bugs. When one of us changed a screen or system, the other needed to be able to understand what had changed and why.

Our working notes, task tracking, decisions, changelog, risk notes and release checklist are kept in [`project_management/`](project_management/README.md). It's a small system, but one we could actually live with.

There is also a rule about not farting when we're working together in person. This is, somehow, one of the less controversial decisions in the project.

## Resources and AI Use

Useful references and tools included:

- [Python documentation](https://docs.python.org/3/) — Python syntax, standard library and error handling.
- [Pygame documentation](https://pyga.me/docs/) — surfaces, events, drawing and input.
- [MiniLibX documentation](https://harm-smits.github.io/42docs/libs/minilibx) — understanding the image/window/pixel operations used for the graphics-equivalence analysis.
- [pytest documentation](https://docs.pytest.org/) — automated testing.
- [mypy documentation](https://mypy.readthedocs.io/) and [flake8 documentation](https://flake8.pycqa.org/) — static checks and code style.
- [uv documentation](https://docs.astral.sh/uv/) — environment and dependency management.
- The **42 Pacman subject (version 1.5)** and our assigned **A-Maze-ing** package — the requirements and generator interface that shaped the implementation.

We used AI as a development assistant, not as a replacement for understanding the project. It helped us work through architecture choices, debug Python and Pygame behaviour, reason about algorithms and edge cases, suggest tests, draft documentation, and explore artwork and interface ideas. Some suggestions were useful immediately; others needed correcting or discarding. We reviewed, adjusted and tested the results ourselves, and we take responsibility for the code and choices in the repository.

The most useful thing AI did was often help explain *why* something broke. The least useful thing was occasionally being extremely confident about a thing that was still broken. An excellent reminder that verification is not optional.

---

**Made by ikolokou and rrasmuss at 42 Berlin.**

Two queens enter. Four ghosts regret their life choices.
