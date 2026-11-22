# Changelog / highlights

Not every commit, just the parts that changed what we could play or see.

## 3–11 October — Foundation

- Planned a modular Python game with separate generator, gameplay, and presentation responsibilities.
- Began turning the subject into a workable game architecture and sequence of tasks.

## 12–25 October — Gameplay first

- Worked through maze navigation, movement, ghost behaviour and scoring logic.
- Expanded testing around predictable seeds and awkward maze layouts.
- Kept refactoring focused on actual responsibilities.

## 26 October–8 November — A proper game starts emerging

- Integrated ghosts and frightened-state behaviour into level gameplay.
- Improved level and maze interactions, including placement edge cases tracked for later verification.
- Developed the drag-themed presentation and character assets.

## 9–15 November — More screens, fewer secret buttons

- Replaced scattered cheat hotkeys with a visible cheat panel.
- Developed the main-menu and character presentation.
- Continued screen flow, testing and game-state integration.

## 16–21 November — Final flow and pixel surgery

- Worked on score entry / leaderboard presentation and Game Over flow.
- Added the Game Over mercy interaction and funeral artwork.
- Replaced higher-level image scaling with direct pixel sampling.
- Reworked startup fading and grayscale calculations to operate on image pixels.
- Fixed the Game Over display issue by writing the computed grayscale colours directly to the canvas.
- Reviewed Pygame blending flags and documented their equivalent pixel mathematics.
- Continued parallel work on frightened ghosts, pause presentation and Victory.

## Still upcoming

- Final merge and playthrough.
- Finish mandatory edge-case review.
- Subject-based submission checklist, README, packaging and release.
