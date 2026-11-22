# 42 subject / things we must be able to demonstrate

Working checklist based on our reading of the 42 Pac-Man subject. This is a practical checklist, **not a substitute for the original PDF**. Final acceptance means checking against that PDF and the final code.

| Area | What we need | Status |
| --- | --- | --- |
| Language / structure | Python 3.10+, object-oriented design | Developed; final review |
| External generator | Use supplied A-Maze-ing generator without modifying it | Verify final package |
| Configuration | Read JSON configuration, handle invalid/missing values and comments | Test edge cases |
| Game loop | Working movement, valid maze, controls, HUD and timer | Playthrough |
| Ghosts | Behaviour, frightened state, collisions | Integration check |
| Pacgums | Regular and four super-pacgums on valid, reachable cells | Check fallback logic |
| Progression | At least ten levels, lives, scoring, Game Over and Victory | Full playthrough |
| Highscores | Persistent top ten, safe entry and score validation | Final combined build |
| Graphics | Each used graphics capability defensible via MiniLibX equivalents | Final source audit |
| Collaboration | Task planning, shared decisions, division of work and progress record | This folder |
| README | Clear setup, controls, design/technical explanations | Finish main README |
| Release | Free, unlisted itch.io build and required submission materials | Not yet confirmed |

## Some details that are easy to miss

- Highscore name input: subject permits up to 10 alphanumeric/space characters; our UI uses **three A–Z initials** by design.
- Score records must be valid and persistent. A cheat-assisted result should not count as a legitimate achievement.
- We should show that the game works with configuration changes, not only with the configuration we used while building it.
- The maze generator is supplied by the project; we wrap it, we don't rewrite it.
- For graphics, the subject asks for equivalents to MiniLibX operations. Our notes explain image scaling, fading and blending in plain language, with pixel-buffer arithmetic at the centre.
- Delivery is more than 'it runs locally': README, usable launch instructions, project-management evidence and the required public build need checking.

## Where the requirements connect to our work

- Generator and maze: `game/` and adapter code.
- Menu / application state: `app/`.
- Highscores, scores, game states: dedicated application/game modules.
- Automated tests: `tests/`.
- Graphics choices: main README's *Graphics Challenges* section and our decision log.

**Final check:** Compare each line with the project's own `en.subject.pdf` before submission. This file is a tracking aid, not a claim of certification.
