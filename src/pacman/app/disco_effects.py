
"""Render decorative disco effects for Fabulous Mode."""

import colorsys
import math

import pygame as pg


class DiscoEffects:
    """Draw mirrored disco balls and animated rainbow lighting."""

    BALL_RADIUS = 34
    BALL_MARGIN = 12
    LIGHT_OPACITY = 105

    def _rainbow_colour(
        self,
        hue: float,
    ) -> tuple[int, int, int]:
        """Convert a hue into a bright RGB colour."""
        red, green, blue = colorsys.hsv_to_rgb(
            hue % 1.0, 0.95, 1.0
        )
        return (
            round(red * 255),
            round(green * 255),
            round(blue * 255),
        )

    def _ball_positions(
        self,
        screen: pg.Surface,
        maze_bounds: pg.Rect,
    ) -> list[tuple[int, int]]:
        """Find four positions around the maze corners."""
        distance = self.BALL_RADIUS + self.BALL_MARGIN

        candidates = [
            (
                maze_bounds.left - distance,
                maze_bounds.top - distance,
            ),
            (
                maze_bounds.right + distance,
                maze_bounds.top - distance,
            ),
            (
                maze_bounds.left - distance,
                maze_bounds.bottom + distance,
            ),
            (
                maze_bounds.right + distance,
                maze_bounds.bottom + distance,
            ),
        ]

        radius = self.BALL_RADIUS
        width, height = screen.get_size()

        # Keep decorations outside the maze and inside the display.
        return [
            (x, y)
            for x, y in candidates
            if radius <= x <= width - radius
            and radius <= y <= height - radius
        ]

    def _draw_rainbow_lights(
        self,
        screen: pg.Surface,
        maze_bounds: pg.Rect,
        positions: list[tuple[int, int]],
        animation_time: float,
    ) -> None:
        """Project bright, smoothly moving rainbow spotlights."""
        lighting = pg.Surface(screen.get_size(), pg.SRCALPHA)
        lighting.set_clip(maze_bounds.clip(screen.get_rect()))

        centre = pg.Vector2(maze_bounds.center)
        beam_length = max(
            maze_bounds.width,
            maze_bounds.height,
        ) * 1.5

        for ball_index, position in enumerate(positions):
            origin = pg.Vector2(position)
            direction = centre - origin

            if direction.length_squared() == 0:
                continue

            direction = direction.normalize()
            perpendicular = pg.Vector2(
                -direction.y,
                direction.x,
            )

            for beam_index in range(7):
                # Each beam moves at a slightly different phase.
                phase = (
                    animation_time * 0.14
                    + ball_index * 0.19
                    + beam_index / 7
                )
                colour = self._rainbow_colour(phase)

                sway = math.sin(
                    animation_time * 0.65
                    + beam_index * 0.8
                    + ball_index
                )

                spread = (
                    (beam_index - 3) * 50
                    + sway * 65
                )

                target = (
                    origin
                    + direction * beam_length
                    + perpendicular * spread
                )

                # Wide overlapping triangles make the lights visible.
                beam_width = 55
                left_edge = target + perpendicular * beam_width
                right_edge = target - perpendicular * beam_width

                points: list[tuple[float, float]] = [
                    (float(position[0]), float(position[1])),
                    (left_edge.x, left_edge.y),
                    (right_edge.x, right_edge.y),
                ]

                pg.draw.polygon(
                    lighting,
                    (*colour, self.LIGHT_OPACITY),
                    points,
                )

                # A soft coloured pool adds moving reflections.
                reflection = centre + perpendicular * spread
                pg.draw.circle(
                    lighting,
                    (*colour, 48),
                    (round(reflection.x), round(reflection.y)),
                    55,
                )

        screen.blit(lighting, (0, 0))

    def _draw_disco_ball(
        self,
        screen: pg.Surface,
        position: tuple[int, int],
        animation_time: float,
    ) -> None:
        """Draw a silver mirror ball with animated reflective tiles."""
        radius = self.BALL_RADIUS
        size = radius * 2 + 2
        centre = (radius + 1, radius + 1)

        ball = pg.Surface((size, size), pg.SRCALPHA)

        # A dark circular backing gives the silver facets depth.
        pg.draw.circle(
            ball,
            (65, 65, 85),
            centre,
            radius,
        )

        tile_size = 9
        rotation = math.sin(animation_time * 0.8) * 5

        # Build a grid of square mirrored facets.
        for tile_y in range(0, size, tile_size):
            for tile_x in range(0, size, tile_size):
                dx = tile_x + tile_size / 2 - centre[0]
                dy = tile_y + tile_size / 2 - centre[1]

                if dx * dx + dy * dy >= (radius - 3) ** 2:
                    continue

                # A moving brightness pattern suggests rotation.
                shimmer = math.sin(
                    tile_x * 0.22
                    + tile_y * 0.14
                    + animation_time * 1.5
                    + rotation
                )

                brightness = round(165 + shimmer * 65)
                brightness = max(75, min(255, brightness))

                colour = (
                    brightness,
                    brightness,
                    min(255, brightness + 12),
                )

                tile = pg.Rect(
                    tile_x + 1,
                    tile_y + 1,
                    tile_size - 2,
                    tile_size - 2,
                )
                pg.draw.rect(ball, colour, tile)

        # Mask the mirrored grid to maintain a round silhouette.
        mask = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.circle(
            mask,
            (255, 255, 255, 255),
            centre,
            radius,
        )
        ball.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        # Bright edge and specular highlights reinforce the shape.
        pg.draw.circle(
            ball,
            (225, 225, 245),
            centre,
            radius,
            2,
        )
        pg.draw.circle(
            ball,
            (255, 255, 255),
            (centre[0] - 12, centre[1] - 13),
            5,
        )

        screen.blit(
            ball,
            (
                position[0] - radius - 1,
                position[1] - radius - 1,
            ),
        )

        # A hanging wire helps identify the object as a disco ball.
        pg.draw.line(
            screen,
            (200, 200, 220),
            (position[0], position[1] - radius),
            (position[0], position[1] - radius - 12),
            2,
        )

    def render(
        self,
        screen: pg.Surface,
        maze_bounds: pg.Rect,
        animation_time: float,
    ) -> None:
        """Render the disco balls and their rainbow lighting."""
        positions = self._ball_positions(screen, maze_bounds)

        # Draw light first so the mirror balls remain in front.
        self._draw_rainbow_lights(
            screen,
            maze_bounds,
            positions,
            animation_time,
        )

        for position in positions:
            self._draw_disco_ball(
                screen,
                position,
                animation_time,
            )
