from dataclasses import dataclass
from typing import Optional

from config.loader import Config
from game.ghost import Ghost
from game.level import build_level_maze
from game.maze_loader import Maze
from game.player import Player


@dataclass
class GameState:
    """Everything that makes up a running game, independent of display."""

    config: Config
    level_index: int
    maze: Maze
    player: Player
    ghosts: list[Ghost]

    @classmethod
    def new_game(cls, config: Config) -> "GameState":
        maze = build_level_maze(config, level_index=0)
        return cls(
            config=config,
            level_index=0,
            maze=maze,
            player=Player.at_center(maze, lives=config.lives),
            ghosts=[Ghost.at_cell(*maze.entry)],
        )

    def update(self, dt: float, direction: Optional[str]) -> None:
        """Advance the game by `dt` seconds. `direction` is the move the
        player is asking for this frame, if any."""
        if direction is not None:
            self.player.try_start_move(direction, self.maze)
        self.player.update(dt)
        for ghost in self.ghosts:
            ghost.update_in(self.maze, dt)
