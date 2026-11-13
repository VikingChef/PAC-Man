
"""Calculate how a game canvas fits inside a display."""

import pygame as pg


# Keep gameplay coordinates independent of the physical monitor.
# The finished canvas will be scaled proportionally to fit the display.
GAME_WIDTH = 1920
GAME_HEIGHT = 1440

# Menus use a widescreen layout, separate from the taller game canvas.
# The animated background will still cover the physical display.
MENU_WIDTH = 1920
MENU_HEIGHT = 1080

# Reserve space above the maze for score, timer, lives and level.
# This prevents the HUD from covering gameplay elements.
HUD_HEIGHT = 120

# Leave room around the maze for Fabulous Mode's disco balls.
# The margin also accommodates their hanging wires.
MAZE_MARGIN = 100


def fit_canvas(
    canvas_size: tuple[int, int],
    display_size: tuple[int, int],
) -> tuple[float, tuple[int, int]]:
    """Return the scale and position for a fitted canvas."""

    # Separate the logical game dimensions from the physical display.
    # The game canvas keeps its proportions on every screen.
    canvas_width, canvas_height = canvas_size
    display_width, display_height = display_size

    # Calculate how much we can scale the canvas in each direction.
    # These values may differ when the screen has another aspect ratio.
    width_scale = display_width / canvas_width
    height_scale = display_height / canvas_height

    # Use the smaller factor so the entire canvas remains visible.
    # Applying one factor to both dimensions prevents stretching.
    scale = min(width_scale, height_scale)

    # Calculate the dimensions of the canvas after scaling.
    # Pygame requires whole pixel dimensions for its surfaces.
    scaled_width = round(canvas_width * scale)
    scaled_height = round(canvas_height * scale)

    # Centre the fitted canvas within any unused display space.
    # Integer division produces whole-pixel drawing coordinates.
    x = (display_width - scaled_width) // 2
    y = (display_height - scaled_height) // 2

    return scale, (x, y)


def maze_origin(maze_size: tuple[int, int]) -> tuple[int, int]:
    """Centre the maze in the space below the HUD."""

    maze_width, maze_height = maze_size

    # The maze is centred horizontally across the full canvas.
    maze_x = (GAME_WIDTH - maze_width) // 2

    # Only the area below the HUD is available for gameplay.
    # This prevents the maze from overlapping the top bar.
    available_height = GAME_HEIGHT - HUD_HEIGHT

    # Centre vertically within that remaining gameplay area.
    # Add HUD_HEIGHT because the area starts below the HUD.
    maze_y = (
        HUD_HEIGHT
        + (available_height - maze_height) // 2
    )

    return maze_x, maze_y


def render_canvas(
    canvas: pg.Surface,
    display: pg.Surface,
) -> None:
    """Scale and centre the game canvas on the physical display."""

    # Calculate how the canvas fits without distorting its proportions.
    scale, (x, y) = fit_canvas(
        canvas.get_size(),
        display.get_size(),
    )

    # Pygame needs whole pixel dimensions for the scaled image.
    canvas_width, canvas_height = canvas.get_size()
    scaled_size = (
        round(canvas_width * scale),
        round(canvas_height * scale),
    )

    # Clear unused screen space so previous frames cannot remain visible.
    # The dark background will eventually match our gameplay artwork.
    display.fill((24, 18, 38))

    # Resize the completed game image while preserving its aspect ratio.
    scaled_canvas = pg.transform.smoothscale(canvas, scaled_size)

    # Place the scaled image in the centre of the physical display.
    display.blit(scaled_canvas, (x, y))


def screen_to_canvas(
    screen_position: tuple[int, int],
    canvas_size: tuple[int, int],
    display_size: tuple[int, int],
) -> tuple[int, int] | None:
    """Convert a physical mouse position into canvas coordinates."""

    # Use the same scale and offset as the rendering function.
    # Mouse clicks must match where the game is actually displayed.
    scale, (offset_x, offset_y) = fit_canvas(
        canvas_size,
        display_size,
    )

    # Translate the mouse position relative to the scaled canvas.
    mouse_x = screen_position[0] - offset_x
    mouse_y = screen_position[1] - offset_y

    # Ignore clicks in the unused margins around the game.
    scaled_width = round(canvas_size[0] * scale)
    scaled_height = round(canvas_size[1] * scale)

    if not (0 <= mouse_x < scaled_width):
        return None

    if not (0 <= mouse_y < scaled_height):
        return None

    # Undo the scaling to recover the original canvas coordinates.
    canvas_x = int(mouse_x / scale)
    canvas_y = int(mouse_y / scale)

    return canvas_x, canvas_y
