"""Cheat mode, meant to let reviewers test every feature quickly.

The mode is switched on and off as a whole; once on, each cheat can be
used. Toggle cheats stay active until used again; the others act once.
"""
from dataclasses import dataclass
from enum import Enum


class Cheat(Enum):
    """The available cheats."""

    INVINCIBLE = "invincible"    # toggle: hunting ghosts cannot hurt
    SKIP_LEVEL = "skip_level"    # once: the current level is won
    FREEZE_GHOSTS = "freeze"     # toggle: ghosts stop moving
    EXTRA_LIFE = "extra_life"    # once: +1 life
    FAST = "fast"                # toggle: player moves twice as fast
    FRIGHTEN = "frighten"        # once: ghosts become edible


@dataclass
class CheatState:
    """Whether cheat mode is on, and which toggle cheats are active."""

    enabled: bool = False
    invincible: bool = False
    ghosts_frozen: bool = False
    fast: bool = False

    def active_labels(self) -> list[str]:
        """Short names of the active toggle cheats, for the HUD."""
        labels = []
        if self.invincible:
            labels.append("INVINCIBLE")
        if self.ghosts_frozen:
            labels.append("FROZEN")
        if self.fast:
            labels.append("FAST")
        return labels
