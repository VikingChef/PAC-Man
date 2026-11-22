# Last checks before we send Pac-Ma'am into the world

## Build

- [ ] Merge our branches intentionally. No mystery changes in `main`.
- [ ] `uv sync` succeeds on a clean machine.
- [ ] `make lint` passes.
- [ ] `uv run pytest -q` passes.
- [ ] `make run` launches.
- [ ] No temporary debug images, test saves or leftover print statements.

## Actually play the game

- [ ] Start, choose a queen, play, pause and resume.
- [ ] Check maze placement, all ghost modes, deaths and frightened effects.
- [ ] Confirm level transitions up to at least level 10.
- [ ] Check mercy, Game Over, Victory and the return to menu.
- [ ] Confirm highscores save/load and name entry behave properly.
- [ ] Try strange configuration values and at least a few different seeds.
- [ ] Check normal/hover artwork, transparency and game window sizing.
- [ ] Ensure visual cheats don't accidentally create legitimate score records.

## Compliance and handover

- [ ] Read the final subject again. Check each requirement, not just the exciting ones.
- [ ] Confirm graphic operations match the team's MiniLibX-equivalence rationale.
- [ ] Main README explains installation, controls, design and graphics challenges.
- [ ] Include project-management folder in final repository.
- [ ] Prepare the requested free/unlisted itch.io build.
- [ ] Demonstrate the game from a clean launch without editing code live.

**Release criterion:** Both of us can sit down, launch the thing, and explain the choices without inventing an answer on the spot.
