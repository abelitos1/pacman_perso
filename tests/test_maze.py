"""Tests of maze loading and level layout."""
import unittest

from config.loader import load_config
from game.entity import DIRECTIONS, can_step
from game.level import build_level, reachable_cells


class LevelLayoutTest(unittest.TestCase):
    """Every level of the shipped config is well formed."""

    def setUp(self) -> None:
        """Load the project config."""
        self.config = load_config("config.json")

    def test_level_one_is_deterministic(self) -> None:
        """Level 1 uses the config seed: two builds give the same maze."""
        first = build_level(self.config, 0).maze.cells
        second = build_level(self.config, 0).maze.cells
        self.assertEqual(first, second)

    def test_every_level_is_playable(self) -> None:
        """Spawn, corners and pacgums are all reachable cells."""
        for index in range(len(self.config.levels)):
            layout = build_level(self.config, index)
            reachable = reachable_cells(layout.maze, layout.player_spawn)
            self.assertEqual(len(layout.ghost_homes), 4)
            self.assertTrue(set(layout.ghost_homes) <= reachable)
            self.assertEqual(layout.super_pacgums, set(layout.ghost_homes))
            self.assertEqual(layout.pacgums | layout.super_pacgums
                             | {layout.player_spawn}, reachable)

    def test_walls_are_consistent(self) -> None:
        """A step allowed one way is allowed back (no one-way walls)."""
        maze = build_level(self.config, 0).maze
        back = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT",
                "RIGHT": "LEFT"}
        for y in range(maze.height):
            for x in range(maze.width):
                for d, (dx, dy) in DIRECTIONS.items():
                    if can_step(maze, x, y, d):
                        self.assertTrue(
                            can_step(maze, x + dx, y + dy, back[d]))


if __name__ == "__main__":
    unittest.main()
