"""Drawing of the characters (Pac-Man, ghosts) and of the pacgums."""
import math
from typing import Iterable

import pygame

from game.entity import DIRECTIONS
from game.ghost import Ghost
from game.maze_loader import Coord
from game.player import Player

PLAYER_COLOR = (255, 255, 0)
EYE_WHITE = (255, 255, 255)
EYE_PUPIL = (0, 0, 180)
PACGUM_COLOR = (255, 200, 150)
FRIGHTENED_COLOR = (33, 33, 255)
FRIGHTENED_FLASH_COLOR = (230, 230, 255)
MOUTH_MAX = 40.0  # half-opening of the mouth, in degrees
CHOMP_SPEED = 14.0
FACING_ANGLE = {"RIGHT": 0.0, "UP": 90.0, "LEFT": 180.0, "DOWN": 270.0}


def _cell_center(x: float, y: float, cell_size: int) -> tuple[int, int]:
    """Pixel center of (possibly fractional) cell (x, y)."""
    return (int(x * cell_size + cell_size / 2),
            int(y * cell_size + cell_size / 2))


def draw_pacgums(surface: pygame.Surface, pacgums: Iterable[Coord],
                 super_pacgums: Iterable[Coord], cell_size: int,
                 elapsed: float) -> None:
    """Small dots for pacgums, big pulsing ones for super-pacgums."""
    small = max(2, int(cell_size * 0.1))
    for x, y in pacgums:
        pygame.draw.circle(surface, PACGUM_COLOR,
                           _cell_center(x, y, cell_size), small)
    pulse = 0.22 + 0.06 * abs((elapsed * 2) % 2 - 1)
    big = max(3, int(cell_size * pulse))
    for x, y in super_pacgums:
        pygame.draw.circle(surface, PACGUM_COLOR,
                           _cell_center(x, y, cell_size), big)


def draw_player(surface: pygame.Surface, player: Player, cell_size: int,
                elapsed: float) -> None:
    """Pac-Man: a yellow disc with a mouth facing where he goes, which
    chomps while he moves.

    The body is drawn as a "pie" polygon: the center, then points on the
    circle from one lip (facing + mouth) all the way round to the other
    lip (facing - mouth). `mouth` is the half-opening angle in degrees.
    """
    cx, cy = _cell_center(player.x, player.y, cell_size)
    radius = cell_size / 2 * 0.7
    if player.is_moving():
        mouth = MOUTH_MAX * abs(math.sin(elapsed * CHOMP_SPEED))
    else:
        mouth = MOUTH_MAX / 2
    facing = FACING_ANGLE[player.facing]
    points = [(float(cx), float(cy))]
    steps = 24
    for i in range(steps + 1):
        angle = math.radians(facing + mouth
                             + (360 - 2 * mouth) * i / steps)
        # minus on y: screen y grows downward, angles are counter-clockwise
        points.append((cx + radius * math.cos(angle),
                       cy - radius * math.sin(angle)))
    pygame.draw.polygon(surface, PLAYER_COLOR, points)


def draw_ghost(surface: pygame.Surface, ghost: Ghost, cell_size: int,
               flash: bool = False) -> None:
    """Classic ghost: round head, straight body, wavy skirt, eyes that
    look in the direction it's moving.

    An edible ghost is drawn blue (flashing white when `flash` is set,
    i.e. when edible mode is about to end). An eaten ghost is not drawn.
    """
    if ghost.is_eaten:
        return
    color = ghost.color
    if ghost.edible:
        color = FRIGHTENED_FLASH_COLOR if flash else FRIGHTENED_COLOR
    cx = ghost.x * cell_size + cell_size / 2
    cy = ghost.y * cell_size + cell_size / 2
    r = cell_size / 2 * 0.7
    left, right = cx - r, cx + r
    bottom = cy + r

    # head: a disc; body: a polygon from the middle of the head down to a
    # zigzag bottom edge alternating between `bottom` and a bit higher
    pygame.draw.circle(surface, color, (int(cx), int(cy)), int(r))
    points = [(left, cy), (left, bottom)]
    teeth = 3
    for i in range(1, 2 * teeth + 1):
        depth = bottom - r * 0.3 if i % 2 else bottom
        points.append((left + i * r / teeth, depth))
    points.append((right, cy))
    pygame.draw.polygon(surface, color, points)

    # pupils are shifted toward the movement direction
    dx, dy = DIRECTIONS[ghost.direction]
    for side in (-1, 1):
        ex, ey = cx + side * r * 0.4, cy - r * 0.15
        pygame.draw.circle(surface, EYE_WHITE,
                           (int(ex), int(ey)), int(r * 0.3))
        pygame.draw.circle(surface, EYE_PUPIL,
                           (int(ex + dx * r * 0.13), int(ey + dy * r * 0.13)),
                           int(r * 0.15))
