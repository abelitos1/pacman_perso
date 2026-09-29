from dataclasses import dataclass

from game.entity import GridEntity
from game.maze_loader import Maze


@dataclass
class Player(GridEntity):
    """Pac-Man, steered by the keyboard."""

    lives: int = 3

    @classmethod
    def at_center(cls, maze: Maze, lives: int = 3) -> "Player":
        """Build a Player spawned at the middle of the given maze."""
        cx, cy = maze.width // 2, maze.height // 2
        return cls(cell_x=cx, cell_y=cy, target_x=cx, target_y=cy,
                   lives=lives)

    def respawn(self, maze: Maze) -> None:
        """Reset the player to the center of the maze
        (e.g. after losing a life)."""
        self.place_at(maze.width // 2, maze.height // 2)
