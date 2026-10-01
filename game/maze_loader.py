"""Adapter around the external A-Maze-ing package.

The package is used as-is (it must not be modified): this module only
calls it and converts its output (one wall bitmask per cell) into our
own Maze / Cell types, so the rest of the game never depends on it.
"""
from dataclasses import dataclass
from typing import Optional

from mazegenerator import MazeGenerator

Coord = tuple[int, int]

# bits of a cell value in the generator output: a set bit is a wall
WALL_N, WALL_E, WALL_S, WALL_W = 1, 2, 4, 8


class MazeGenerationError(Exception):
    """Raised when the A-Maze-ing package fails to build a maze."""


@dataclass
class Cell:
    """Walls around one maze cell."""

    wall_north: bool
    wall_east: bool
    wall_south: bool
    wall_west: bool


@dataclass
class Maze:
    """Maze grid, indexed as cells[y][x]."""

    width: int
    height: int
    cells: list[list[Cell]]
    entry: Coord
    exit: Coord


class MazeLoader:
    """Adapter from the external MazeGenerator to our Maze type."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Coord,
        exit: Coord,
        seed: Optional[int] = None,
        perfect: bool = False,
    ) -> None:
        """Store the generation parameters (seed None means 0)."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.seed = seed if seed is not None else 0
        self.perfect = perfect

    def load(self) -> Maze:
        """Run the generator and convert its output.

        Raises:
            MazeGenerationError: If the generator fails.
        """
        try:
            generator = MazeGenerator(
                size=(self.width, self.height),
                perfect=self.perfect,
                entry_cell=self.entry,
                exit_cell=self.exit,
                seed=self.seed,
            )
        except Exception as err:
            # external code: any failure must end as a clean message
            raise MazeGenerationError(
                f"Maze generation failed: {err}") from err

        return self._convert(generator)

    def _convert(self, generator: MazeGenerator) -> Maze:
        """Turn the generator's wall bitmasks into Cell objects."""
        cells = [
            [
                Cell(
                    wall_north=bool(value & WALL_N),
                    wall_east=bool(value & WALL_E),
                    wall_south=bool(value & WALL_S),
                    wall_west=bool(value & WALL_W),
                )
                for value in row
            ]
            for row in generator.maze
        ]
        return Maze(
            width=self.width,
            height=self.height,
            cells=cells,
            entry=generator.maze_entry,
            exit=generator.maze_exit,
        )
