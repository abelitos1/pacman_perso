from dataclasses import dataclass

from game.maze_loader import Maze

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
        return self.cell_y + (self.target_y - self.cell_y) * self.progress

    def is_moving(self) -> bool:
        return (self.cell_x, self.cell_y) != (self.target_x, self.target_y)

    def can_move(self, direction: str, maze: Maze) -> bool:
        """True if no wall or maze border blocks `direction` from here."""
        if direction not in DIRECTIONS:
            return False
        cell = maze.cells[self.cell_y][self.cell_x]
        if getattr(cell, WALL_ATTR_BY_DIRECTION[direction]):
            return False
        dx, dy = DIRECTIONS[direction]
        next_x, next_y = self.cell_x + dx, self.cell_y + dy
        return 0 <= next_x < maze.width and 0 <= next_y < maze.height

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

    def update(self, dt: float) -> None:
        """Advance the current hop, if any, by `dt` seconds."""
        if not self.is_moving():
            return

        self.progress += self.speed * dt
        if self.progress >= 1.0:
            self.cell_x, self.cell_y = self.target_x, self.target_y
            self.progress = 0.0

    def place_at(self, x: int, y: int) -> None:
        """Teleport to cell (x, y), cancelling any hop in progress."""
        self.cell_x = self.target_x = x
        self.cell_y = self.target_y = y
        self.progress = 0.0
