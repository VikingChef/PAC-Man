# Task board — 21 November 2026

This is the shared snapshot. Before calling something finished for release, check the **merged** branch.

## Done / working in development

- [x] Core Pac-Man player/maze/ghost architecture and playable game loop.
- [x] Project split into smaller, clearer gameplay and presentation modules.
- [x] Cheat panel with explicit controls.
- [x] Character selection and Brunhilda / Power Pellet presentation work.
- [x] Game Over with mercy decision and themed art.
- [x] Highscore screens and initials flow developed.
- [x] Direct pixel scaling introduced for graphics compatibility.
- [x] Startup fade and Game Over grayscale changed to direct pixel operations.
- [x] Agreed documentation argument for retained additive/multiplicative blending.

## In progress / waiting on integration

- [ ] Confirm Ilias's frightened-ghost visual changes in the combined game.
- [ ] Confirm Victory screen and return flow on the merged branch.
- [ ] Confirm pause menu and all menu assets after integration.
- [ ] Finish/finally verify the graphics audit against the actual source.

## Still needs a proper final check

- [ ] Ghost corner spawn fallback when a corner is blocked.
- [ ] Super-pacgum nearest reachable corner fallback.
- [ ] Normal pacgums only on distinct, reachable, non-reserved cells.
- [ ] Ten playable levels and timer / lives / score transitions.
- [ ] Configuration input, invalid values and comments.
- [ ] Top ten highscore persistence, initials validation, cheat-score exclusion.
- [ ] Fresh install, automated tests, lint and complete playthrough.
- [ ] README, public free/unlisted itch.io packaging, submission contents.

**Rule:** An unchecked box isn't an accusation. It's simply something we haven't signed off on together in the final build.
