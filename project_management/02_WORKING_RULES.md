# Working agreement

*Rasmus & Ilias. Two developers. One game. Minimal paperwork.*

1. **Talk first if a change affects both of us.** Especially application flow, assets, and anything already being edited on another branch.
2. **Don't experiment on `main`.** Use separate branches and merge when the change behaves.
3. **A test isn't a screenshot.** Run automated checks for logic; actually launch the game for UI, animations, hitboxes and transitions.
4. **Don't silently redesign approved artwork.** If we agree on a look, preserve it unless we agree to change it.
5. **Keep the code readable.** Sensible names, small responsibilities, one-line docstrings where possible, maximum 79 characters per line, flake8/mypy/pytest.
6. **Say what broke.** 'It doesn't work' is a starting point, not a bug report. What happened, what should have happened, and how to reproduce it?
7. **NO FARTING WHEN PHYSICALLY WORKING TOGETHER.** Includes silent chemical warfare. Open a window and confess. Blaming ghost AI is not accepted.
8. **Don't make things up in tests or documentation.** If we haven't verified the final build, mark it for checking.
9. **Big rewrites need a reason.** We are not refactoring just because a file has had the audacity to grow.
10. **Have fun.** This is a game about dragqueens in a maze, not a banking backend.

When one of us is away, we leave a short note describing what's changed and which branch it's on. That's enough process for two people.
