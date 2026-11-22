# Weekly notes

Short notes, useful decisions, and the occasional bit of swearing. No meeting-room theatre.

## Saturday 3 October — Starting point

**On our minds:** The subject is bigger than just making a yellow circle eat dots. Maze generation, ghosts, progression, scores and configuration all need their own space.

**Plan:** Get the architecture agreed early. Keep the generator separate from our game logic and build something that can be tested without drawing every frame.

**Next:** Sit down together with the subject and sketch the main pieces before racing into features.

## Week of 5–11 October — Working together

**What we talked through:** Player, level, ghost and maze responsibilities. How the configuration reaches the actual game. Which code can change without disturbing the rest.

**Decision:** Build a small, playable foundation and expand from there. Keep the maze generator wrapped rather than buried inside every class.

**Next:** Get player movement and a game loop feeling right. Then ghosts. One catastrophe at a time.

## Week of 12–18 October — Logic before lipstick

**Focus:** Maze rules, reachable paths, ghosts, scoring and repeatable behaviour.

**Problem:** A random seed is very good at finding assumptions you didn't realise you'd made.

**Decision:** Tests should cover fixed inputs and edge cases, not just one maze that happened to behave nicely.

**Next:** Keep checking awkward spawns and placement, especially corners and inaccessible tiles.

## Week of 19–25 October — More pieces, less spaghetti

**Focus:** Separating display and game logic. The game has enough moving parts that stuffing everything into the application controller is becoming a bad hobby.

**Decision:** Extract responsibilities when there's a real reason, not just to chase shorter files. Keep interfaces between gameplay and presentation clear.

**Next:** Get the full level loop stable and make sure graphics work can happen without trampling ghost logic.

## Week of 26 October–1 November — Mazes, ghosts, levels

**Focus:** Ghost placement and frightened behaviour; make levels playable and deterministic enough to test.

**Noted:** Corner positions are not always reachable. A seed passing once is not proof the placement logic is correct.

**Next:** Review fallback placement for ghosts and super-pacgums, plus normal pacgums only in reachable, available cells. Keep these on the board until genuinely checked.

## Week of 2–8 November — Make it look like our game

**Focus:** Character identity, menu presentation and bringing core gameplay and the graphics together.

**Decision:** The drag/Viking theme stays. We should support more than one character without having separate games hiding behind each choice.

**Next:** Keep working on visuals, screen flow and the unfinished gameplay edge cases. Also, remember that 'looks nice' doesn't mean the buttons work.

## Week of 9–15 November — The menu has opinions

**Focus:** Themed assets, cheat interface, application flow and tests. We want the game to be playable without secret keyboard rituals.

**Decision:** Put the cheats in a visible panel; keep legitimate high scores separate from score-changing cheat behaviour. Freeze character appearance once approved.

**Next:** Make sure menus, transitions and Game Over/score flows work together. Test clicks as well as keyboard input.

## Week of 16–21 November — The finishing work is still work

**Focus:** Game Over, highscores, visual polish, parallel UI features and graphics compliance. The grayscale funeral screen caused an irritating detour.

**What we learned:** Correct colour calculations can still look wrong if the final surface doesn't draw the way we think. We got the grey back by writing the processed colours directly into the canvas.

**Decision:** Keep graphics-compliance fixes on a separate branch. Retain the two existing blend effects with a clear explanation of how their result can be reproduced through MiniLibX-style pixel operations.

**Next:** Check the final combined version, especially Ilias's frightened ghosts / Victory changes, verify the subject requirements, and package the thing. Not everything that works separately works after a merge.
