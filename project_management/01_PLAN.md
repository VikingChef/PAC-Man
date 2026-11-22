# Plan / 3 October 2026

## What are we making?

A complete Pac-Man-style game in Python, built around the supplied A-Maze-ing generator, with the required levels, player/ghost behaviour, scorekeeping and configuration. Then we gave it an unnecessarily fabulous identity and called it **Pac-Ma'am**.

## Our priorities

1. Make the core game work: maze, movement, collisions, ghosts, pacgums, scoring and level progression.
2. Make it usable: menus, HUD, pause, highscores, Game Over, Victory, instructions.
3. Test the rules and awkward edge cases. Passing tests are nice; a working game is nicer.
4. Check the graphics-library equivalence requirement.
5. README, packaging, release, demonstration. No heroic last-minute surprise refactors.

## Division of work

**Rasmus:** game architecture and integration, maze/gameplay logic, tests, configuration, highscore/game-state flow and graphics-compliance review.

**Ilias:** character and UI artwork, visual presentation, pause and frightened-ghost visuals, Victory work, and testing his own changes before integration.

We both review anything that crosses the boundary. Nobody gets to call a shared file 'mine' forever.

## How we'll work

A small board, separate Git branches for parallel changes, short check-ins. Merge after running tests and looking at the actual screen when we change visuals.

## Rough milestones

- **Early October:** architecture, external maze package, working prototype.
- **Mid/Late October:** gameplay, ghost movement, scoring, configuration, core testing.
- **Early November:** levels and visuals, character integration, better architecture.
- **Mid November:** menus, complete state flow, cheats, highscores and Game Over/Victory.
- **Late November:** compliance, cleanup, README and release checks.

The dates are targets, not a promise to the universe.

## Known risks

The maze generator isn't our code, so we need to handle awkward outputs without modifying it. Ghost/pathfinding bugs can hide in specific seeds. Separate UI work can cause merge conflicts. The graphics requirement is stricter than 'Pygame works on my laptop'. And there's a real risk of spending three days adjusting a button instead of finishing a game.
