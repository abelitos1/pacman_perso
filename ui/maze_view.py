"""Drawing of the maze walls, with their thickness/bend animation."""
import math

import pygame

from game.maze_loader import Maze
from ui.effects import VisualState

WALL_COLOR = (200, 200, 200)

NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
HORIZONTAL, VERTICAL = 0, 1
SPEED_SCALE = 20

WALL_ATTR = {
    NORTH: "wall_north",
    EAST: "wall_east",
    SOUTH: "wall_south",
    WEST: "wall_west",
}


def _phase(x: int, y: int, direction: int, salt: float = 0.0) -> float:
    """Pseudo-random but stable phase in [0, 2*pi) for a wall.

    Classic shader-style hash: the fractional part of a large multiple
    of sin() looks random, but always gives the same value for the same
    wall, so each wall keeps its own rhythm from frame to frame.
    """
    n = math.sin(x * 12.9898 + y * 78.233 + direction * 37.719 + salt)
    n *= 43758.5453
    return (n - math.floor(n)) * 2 * math.pi


def _wall_phase(x: int, y: int, direction: int, chaos: bool,
                salt: float = 0.0) -> float:
    """In chaos mode each wall has its own phase, otherwise all
    horizontal walls move together, and so do all vertical ones."""
    if chaos:
        return _phase(x, y, direction, salt)
    group = HORIZONTAL if direction in (NORTH, SOUTH) else VERTICAL
    return _phase(0, 0, group, salt)


def _wall_segment(px: float, py: float, c: float, direction: int,
                  u: float) -> tuple[tuple[float, float],
                                     tuple[float, float]]:
    """End points of a wall of cell (px, py) of size c, bent by u."""
    if direction == NORTH:
        return (px, py - u), (px + c, py + u)
    if direction == WEST:
        return (px + u, py), (px - u, py + c)
    if direction == SOUTH:
        return (px, py + c - u), (px + c, py + c + u)
    return (px + c + u, py), (px + c - u, py + c)


def draw_maze(screen: pygame.Surface, maze: Maze, cell_size: int,
              stats: VisualState, elapsed: float, scale: float) -> None:
    """Draw every wall of the maze, animated according to `stats`.

    Args:
        screen: Where to draw.
        maze: The maze to draw.
        cell_size: Size of a cell in pixels.
        stats: Current wall animation parameters.
        elapsed: Seconds since the start, drives the animation.
        scale: Multiplier applied to wall thickness and bend.
    """
    # thickness oscillates between thick_l and thick_u, i.e. around
    # their mean with an amplitude of half their difference
    thick_center = (stats.thick_u + stats.thick_l) / 2 * scale
    thick_range = (stats.thick_u - stats.thick_l) / 2 * scale
    bend_amp = stats.bend * scale
    thick_t = elapsed * stats.thick_speed * SPEED_SCALE
    bend_t = elapsed * stats.bend_speed * SPEED_SCALE

    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.cells[y][x]
            px, py = x * cell_size, y * cell_size
            for direction in (NORTH, WEST, SOUTH, EAST):
                if not getattr(cell, WALL_ATTR[direction]):
                    continue
                n = thick_center + thick_range * math.sin(
                    thick_t + _wall_phase(x, y, direction, stats.chaos))
                u = bend_amp * math.sin(
                    bend_t + _wall_phase(x, y, direction, stats.chaos,
                                         salt=99))
                start, end = _wall_segment(px, py, cell_size, direction, u)
                pygame.draw.line(screen, WALL_COLOR, start, end,
                                 max(1, int(n)))
