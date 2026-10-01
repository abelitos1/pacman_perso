"""Grid movement shared by the player and the ghosts.

Every character moves from cell to cell: it is always either resting in
a cell or "hopping" toward a neighbour cell, and walls are checked once,
when a hop starts. The drawn position is interpolated during the hop.
"""
from dataclasses import dataclass

from game.maze_loader import Coord, Maze

DIRECTIONS: dict[str, tuple[int, int]] = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

WALL_ATTR_BY_DIRECTION: dict[str, str] = {
    "UP": "wall_north",
    "DOWN": "wall_south",
    "LEFT": "wall_west",
    "RIGHT": "wall_east",
}

OPPOSITE: dict[str, str] = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}


def can_step(maze: Maze, x: int, y: int, direction: str) -> bool:
    """Tell whether one step in `direction` from cell (x, y) is possible.

    Args:
        maze: The maze to move in.
        x: Column of the starting cell.
        y: Row of the starting cell.
        direction: One of the DIRECTIONS keys.

    Returns:
        True if no wall and no maze border blocks that step.
    """
    if direction not in DIRECTIONS:
        return False
    if getattr(maze.cells[y][x], WALL_ATTR_BY_DIRECTION[direction]):
        return False
    dx, dy = DIRECTIONS[direction]
    return 0 <= x + dx < maze.width and 0 <= y + dy < maze.height


@dataclass
class GridEntity:
    """Something that hops exactly one grid cell at a time, animated smoothly.

    `cell_x`/`cell_y` is the cell the entity is leaving from (or resting
    in, when equal to the target). `target_x`/`target_y` is the cell
    it's gliding toward. `progress` (0..1) is how far along that single
    hop we are. A hop only ever completes exactly at progress == 1.0 --
    there is no rounding of a float position to guess the current cell,
    so there is no ambiguity and no way to tunnel through a wall.
    """

    cell_x: int
    cell_y: int
    target_x: int
    target_y: int
    progress: float = 0.0
    speed: float = 16.0  # cells per second

    @property
    def x(self) -> float:
        """Interpolated position for drawing, between cell and target."""
        return self.cell_x + (self.target_x - self.cell_x) * self.progress

    @property
    def y(self) -> float:
        """Interpolated row for drawing."""
        return self.cell_y + (self.target_y - self.cell_y) * self.progress

    @property
    def nearest_cell(self) -> Coord:
        """Cell the entity is mostly in (the target past half a hop)."""
        if self.progress >= 0.5:
            return (self.target_x, self.target_y)
        return (self.cell_x, self.cell_y)

    def is_moving(self) -> bool:
        """True while a hop toward another cell is in progress."""
        return (self.cell_x, self.cell_y) != (self.target_x, self.target_y)

    def can_move(self, direction: str, maze: Maze) -> bool:
        """True if no wall or maze border blocks `direction` from here."""
        return can_step(maze, self.cell_x, self.cell_y, direction)

    def try_start_move(self, direction: str, maze: Maze) -> bool:
        """Begin a one-cell hop in `direction`, checking the wall once.

        Does nothing (returns False) if already mid-hop or if the move
        is blocked.
        """
        if self.is_moving() or not self.can_move(direction, maze):
            return False
        dx, dy = DIRECTIONS[direction]
        self.target_x, self.target_y = self.cell_x + dx, self.cell_y + dy
        return True

    def update(self, dt: float) -> float:
        """Advance the current hop, if any, by `dt` seconds.

        Returns:
            The time left over when the hop ends before `dt` is used up
            (0.0 otherwise), so the caller can chain the next hop in the
            same frame instead of pausing on each cell.
        """
        if not self.is_moving():
            return 0.0

        self.progress += self.speed * dt
        if self.progress < 1.0:
            return 0.0
        leftover = (self.progress - 1.0) / self.speed
        self.cell_x, self.cell_y = self.target_x, self.target_y
        self.progress = 0.0
        return leftover

    def reverse(self) -> None:
        """Turn back in the middle of a hop, toward the cell just left."""
        if not self.is_moving():
            return
        self.cell_x, self.target_x = self.target_x, self.cell_x
        self.cell_y, self.target_y = self.target_y, self.cell_y
        self.progress = 1.0 - self.progress

    def place_at(self, x: int, y: int) -> None:
        """Teleport to cell (x, y), cancelling any hop in progress."""
        self.cell_x = self.target_x = x
        self.cell_y = self.target_y = y
        self.progress = 0.0
