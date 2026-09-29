"""Keyboard to game direction mapping."""
from typing import Optional, Sequence

import pygame

KEYS_BY_DIRECTION: list[tuple[str, tuple[int, ...]]] = [
    ("UP", (pygame.K_UP, pygame.K_w)),
    ("DOWN", (pygame.K_DOWN, pygame.K_s)),
    ("LEFT", (pygame.K_LEFT, pygame.K_a)),
    ("RIGHT", (pygame.K_RIGHT, pygame.K_d)),
]


def read_direction(pressed: Sequence[bool]) -> Optional[str]:
    """Direction held down this frame (first match wins), or None."""
    for direction, keys in KEYS_BY_DIRECTION:
        if any(pressed[key] for key in keys):
            return direction
    return None
