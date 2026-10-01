"""Ghosts: chase, flee when edible, respawn in their corner when eaten."""
import random
from dataclasses import dataclass, field

from game.entity import DIRECTIONS, OPPOSITE, GridEntity
from game.maze_loader import Coord, Maze

CHASE_SPEED = 6.0  # cells per second
FRIGHTENED_SPEED = 4.0
RESPAWN_DELAY = 5.0  # seconds spent out of the maze once eaten


@dataclass
class Ghost(GridEntity):
    """Ghost moving on its own through the corridors.

    At each cell it picks the next hop, never making a U-turn unless it
    is in a dead end:
      - normally it chases the player: it takes the step that gets
        closest to them, except with probability `randomness` where it
        picks a random corridor (that is what gives each ghost its own
        personality);
      - when `edible`, it runs away: it takes the step that gets
        furthest from the player;
      - once eaten, it leaves the maze for RESPAWN_DELAY seconds, then
        comes back in its home corner.
    At the start of a level (and after a life is lost) it waits in its
    corner for `release_timer` seconds, so the ghosts come out one by one.
    """

    speed: float = CHASE_SPEED
    color: tuple[int, int, int] = (255, 0, 0)
    home: Coord = (0, 0)
    randomness: float = 0.3
    direction: str = "LEFT"
    edible: bool = False
    respawn_timer: float = 0.0
    release_timer: float = 0.0
    rng: random.Random = field(default_factory=random.Random, repr=False)

    @classmethod
    def at_home(cls, home: Coord, color: tuple[int, int, int],
                randomness: float) -> "Ghost":
        """Build a Ghost resting in its home cell."""
        x, y = home
        return cls(cell_x=x, cell_y=y, target_x=x, target_y=y,
                   color=color, home=home, randomness=randomness)

    @property
    def is_eaten(self) -> bool:
        """True while the ghost waits out of the maze to respawn."""
        return self.respawn_timer > 0

    def set_edible(self, edible: bool) -> None:
        """Turn frightened mode on or off (ignored while eaten)."""
        if self.is_eaten:
            return
        self.edible = edible
        self.speed = FRIGHTENED_SPEED if edible else CHASE_SPEED

    def get_eaten(self) -> None:
        """Send the ghost back home, where it waits RESPAWN_DELAY."""
        self.place_at(*self.home)
        self.edible = False
        self.speed = CHASE_SPEED
        self.respawn_timer = RESPAWN_DELAY
        self.release_timer = 0.0

    def reset(self, release_delay: float = 0.0) -> None:
        """Put the ghost back home (e.g. new life).

        Args:
            release_delay: Seconds to wait in the corner before moving.
        """
        self.place_at(*self.home)
        self.edible = False
        self.speed = CHASE_SPEED
        self.respawn_timer = 0.0
        self.release_timer = release_delay

    @property
    def is_waiting(self) -> bool:
        """True while the ghost stays in its corner before moving."""
        return self.release_timer > 0

    def open_directions(self, maze: Maze) -> list[str]:
        """Directions not blocked by a wall or the maze border."""
        return [d for d in DIRECTIONS if self.can_move(d, maze)]

    def _distance_after(self, direction: str, target: Coord) -> int:
        """Manhattan distance to `target` after one step in `direction`."""
        dx, dy = DIRECTIONS[direction]
        return (abs(self.cell_x + dx - target[0])
                + abs(self.cell_y + dy - target[1]))

    def choose_direction(self, maze: Maze, target: Coord) -> None:
        """When resting in a cell, pick the next hop and start it.

        Args:
            maze: The maze to move in.
            target: Cell of the player, to chase or to flee.
        """
        if self.is_moving():
            return
        options = self.open_directions(maze)
        if not options:
            return
        forward = [d for d in options if d != OPPOSITE[self.direction]]
        options = forward or options

        if self.edible:
            self.direction = max(
                options, key=lambda d: self._distance_after(d, target))
        elif self.rng.random() < self.randomness:
            self.direction = self.rng.choice(options)
        else:
            self.direction = min(
                options, key=lambda d: self._distance_after(d, target))
        self.try_start_move(self.direction, maze)

    def update_in(self, maze: Maze, dt: float, target: Coord) -> None:
        """Advance the ghost by `dt` seconds.

        Args:
            maze: The maze to move in.
            dt: Elapsed time in seconds.
            target: Cell of the player.
        """
        if self.is_eaten:
            self.respawn_timer = max(0.0, self.respawn_timer - dt)
            return
        if self.is_waiting:
            self.release_timer = max(0.0, self.release_timer - dt)
            return
        while dt > 0:
            self.choose_direction(maze, target)
            if not self.is_moving():
                return
            dt = self.update(dt)
