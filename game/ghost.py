import random
from dataclasses import dataclass, field

from game.entity import DIRECTIONS, OPPOSITE, GridEntity
from game.maze_loader import Maze


@dataclass
class Ghost(GridEntity):
    """Ghost that wanders the maze at random, one cell hop at a time.

    It has no effect on the game yet: it only moves. At each cell it
    picks a random open direction, avoiding a U-turn unless it is a
    dead end.
    """

    speed: float = 6.0  # cells per second
    color: tuple[int, int, int] = (255, 0, 0)
    direction: str = "LEFT"
    rng: random.Random = field(default_factory=random.Random, repr=False)

    @classmethod
    def at_cell(cls, x: int, y: int) -> "Ghost":
        """Build a Ghost resting in cell (x, y)."""
        return cls(cell_x=x, cell_y=y, target_x=x, target_y=y)

    def open_directions(self, maze: Maze) -> list[str]:
        """Directions not blocked by a wall or the maze border."""
        return [d for d in DIRECTIONS if self.can_move(d, maze)]

    def choose_direction(self, maze: Maze) -> None:
        """When resting in a cell, pick the next hop and start it."""
        if self.is_moving():
            return
        options = self.open_directions(maze)
        if not options:
            return
        forward = [d for d in options if d != OPPOSITE[self.direction]]
        self.direction = self.rng.choice(forward or options)
        self.try_start_move(self.direction, maze)

    def update_in(self, maze: Maze, dt: float) -> None:
        """Advance the current hop, then choose a new one if it ended."""
        self.update(dt)
        self.choose_direction(maze)
