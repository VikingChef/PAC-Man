# Decisions worth keeping

If a choice was expensive to make once, we write it down so we don't make it again on Tuesday.

| When | Choice | Why |
| --- | --- | --- |
| Early October | Separate generator, game rules and display | We need to test the game without relying on a window; generator stays untouched |
| October | Use repeatable seeds in tests | Random mazes hide bugs until the worst possible moment |
| Late October | Split code by responsibility, not arbitrary line count | Readable modules without refactoring as a hobby |
| Early November | Two selectable queens, same underlying game | Different presentation, consistent gameplay |
| November | Keep the approved art approved | Avoid endless redesigns of the same character |
| November | Replace cheat hotkeys with a visible panel | Easier to find, demonstrate and test |
| November | Cheat-assisted results do not enter legitimate highscores | Otherwise disco becomes a competitive advantage |
| Mid November | Three-letter arcade initials for high scores | Retro style and simple entry experience |
| Mid November | One mercy chance on Game Over | A joke that also makes the screen interactive |
| 21 November | Keep compliance experiments on `graphics-compliance` | Avoid collisions with visual work |
| 21 November | Scale/fade with direct pixel calculations | Better match to MiniLibX-style image operations |
| 21 November | Keep additive/multiplicative blend flags | Their effects can be reproduced through basic pixel arithmetic; document the technique |

## One decision we won't repeat

A fixed pixel result means little if the display pipeline then paints over it or composites it incorrectly. For grayscale, the direct canvas pixel write solved what the colour conversion itself could not.
