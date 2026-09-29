"""Keyboard bindings used during the game: moves and cheats."""
from typing import Optional

import pygame

from game.cheats import Cheat

CHEAT_MODE_KEY = pygame.K_TAB

DIRECTION_BY_KEY: dict[int, str] = {
    pygame.K_UP: "UP",
    pygame.K_w: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_s: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_a: "LEFT",
    pygame.K_RIGHT: "RIGHT",
    pygame.K_d: "RIGHT",
}


def direction_for_key(key: int) -> Optional[str]:
    """Game direction bound to `key`, or None if it is not a move key."""
    return DIRECTION_BY_KEY.get(key)


CHEAT_BY_KEY: dict[int, Cheat] = {
    pygame.K_1: Cheat.INVINCIBLE,
    pygame.K_2: Cheat.SKIP_LEVEL,
    pygame.K_3: Cheat.FREEZE_GHOSTS,
    pygame.K_4: Cheat.EXTRA_LIFE,
    pygame.K_5: Cheat.FAST,
    pygame.K_6: Cheat.FRIGHTEN,
}


def cheat_for_key(key: int) -> Optional[Cheat]:
    """Cheat bound to `key` (digit keys 1-6), or None."""
    return CHEAT_BY_KEY.get(key)
