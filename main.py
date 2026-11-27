"""Launch Pac-Ma'am in a web browser."""

import asyncio
import sys
from pathlib import Path

# Pygbag installs third-party browser wheels from top-level imports.
import numpy as np
import pygame
import platform


def browser_log(message: str) -> None:
    """Send browser startup checkpoints to the JavaScript console."""
    if sys.platform != "emscripten":
        return
    # Browser-only console is absent from desktop Python type stubs.
    console = getattr(platform, "console", None)
    if console is not None:
        console.log(message)


async def main() -> None:
    """Start the browser-compatible version of Pac-Ma'am."""
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root / "src"))

    browser_log("PAC-MAAM: main.py started")
    browser_log(f"PAC-MAAM: pygame {pygame.version.ver}")
    browser_log(f"PAC-MAAM: numpy {np.__version__}")

    # Keep the first-party game imports after the browser dependencies.
    browser_log("PAC-MAAM: importing application")
    from pacman.app.application import PacManApp
    from pacman.config.loader import load_config
    browser_log("PAC-MAAM: imports complete")

    config = load_config(project_root / "config.json")
    browser_log("PAC-MAAM: configuration loaded")

    with PacManApp(config) as app:
        browser_log("PAC-MAAM: application initialized")
        await app.run_browser()


if __name__ == "__main__":
    asyncio.run(main())
