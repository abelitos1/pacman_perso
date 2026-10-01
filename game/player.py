"""Pac-Man and his arcade-style controls."""
from dataclasses import dataclass
from typing import Optional

from game.entity import OPPOSITE, GridEntity
from game.maze_loader import Coord, Maze

PLAYER_SPEED = 8.0  # cells per second


@dataclass
class Player(GridEntity):
    """Pac-Man, steered like in the arcade game.

    - A key press sets a direction: there is no need to hold the key,
      Pac-Man keeps going until a wall stops him.
    - A turn asked before reaching a crossing is remembered
      (`next_direction`) and taken as soon as that corridor opens.
    - Turning back is instant, even in the middle of a hop.
    """

    speed: float = PLAYER_SPEED
    lives: int = 3
    direction: Optional[str] = None
    next_direction: Optional[str] = None
    facing: str = "RIGHT"  # last direction moved, for drawing the mouth

    @classmethod
    def at_cell(cls, cell: Coord, lives: int = 3) -> "Player":
        """Build a Player resting in `cell`."""
        x, y = cell
        return cls(cell_x=x, cell_y=y, target_x=x, target_y=y, lives=lives)

    def steer(self, direction: str) -> None:
        """Ask for a direction (from the keyboard)."""
        if (self.is_moving() and self.direction is not None
                and direction == OPPOSITE[self.direction]):
            self.reverse()
            self.direction = self.facing = direction
            self.next_direction = None
        else:
            self.next_direction = direction

    def stop(self) -> None:
        """Forget any move (e.g. after respawning)."""
        self.direction = self.next_direction = None

    def _start_next_hop(self, maze: Maze) -> None:
        """At rest in a cell: take the queued turn if the corridor is
        open, otherwise keep going straight if possible."""
        wanted = self.next_direction
        if wanted is not None and self.can_move(wanted, maze):
            self.direction = wanted
            self.next_direction = None
        if self.direction is not None and self.try_start_move(
                self.direction, maze):
            self.facing = self.direction
        else:
            self.direction = None

    def update_in(self, maze: Maze, dt: float) -> None:
        """Move for `dt` seconds, chaining hops without stopping.

        Args:
            maze: The maze to move in.
            dt: Elapsed time in seconds.
        """
        while dt > 0:
            if not self.is_moving():
                self._start_next_hop(maze)
                if not self.is_moving():
                    return
            dt = self.update(dt)
