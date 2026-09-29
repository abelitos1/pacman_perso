"""Drawing of the moving characters (Pac-Man and ghosts)."""
import pygame

from game.entity import DIRECTIONS
from game.ghost import Ghost
from game.player import Player

PLAYER_COLOR = (255, 255, 0)
EYE_WHITE = (255, 255, 255)
EYE_PUPIL = (0, 0, 180)


def draw_player(surface: pygame.Surface, player: Player,
                cell_size: int) -> None:
    center = (
        int(player.x * cell_size + cell_size / 2),
        int(player.y * cell_size + cell_size / 2),
    )
    radius = int(cell_size / 2 * 0.6)
    pygame.draw.circle(surface, PLAYER_COLOR, center, radius)


def draw_ghost(surface: pygame.Surface, ghost: Ghost,
               cell_size: int) -> None:
    """Classic ghost: round head, straight body, wavy skirt, eyes that
    look in the direction it's moving."""
    cx = ghost.x * cell_size + cell_size / 2
    cy = ghost.y * cell_size + cell_size / 2
    r = cell_size / 2 * 0.7
    left, right = cx - r, cx + r
    bottom = cy + r

    pygame.draw.circle(surface, ghost.color, (int(cx), int(cy)), int(r))
    points = [(left, cy), (left, bottom)]
    teeth = 3
    for i in range(1, 2 * teeth + 1):
        depth = bottom - r * 0.3 if i % 2 else bottom
        points.append((left + i * r / teeth, depth))
    points.append((right, cy))
    pygame.draw.polygon(surface, ghost.color, points)

    dx, dy = DIRECTIONS[ghost.direction]
    for side in (-1, 1):
        ex, ey = cx + side * r * 0.4, cy - r * 0.15
        pygame.draw.circle(surface, EYE_WHITE,
                           (int(ex), int(ey)), int(r * 0.3))
        pygame.draw.circle(surface, EYE_PUPIL,
                           (int(ex + dx * r * 0.13), int(ey + dy * r * 0.13)),
                           int(r * 0.15))
