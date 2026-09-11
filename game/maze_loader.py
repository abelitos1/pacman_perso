from dataclasses import dataclass
from typing import Optional
from mazegenerator import MazeGenerator

Coord = tuple[int, int]

WALL_N, WALL_E, WALL_S, WALL_W = 1, 2, 4, 8


class MazeGenerationError(Exception):
    pass


@dataclass
class Cell:
    wall_north: bool
    wall_east: bool
    wall_south: bool
    wall_west: bool


@dataclass
class Maze:
    width: int
    height: int
    cells: list[list[Cell]]
    entry: Coord
    exit: Coord


class MazeLoader:

    def __init__(
        self,
        width: int,
        height: int,
        entry: Coord,
        exit: Coord,
        seed: Optional[int] = None,
        perfect: bool = False,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.seed = seed if seed is not None else 0
        self.perfect = perfect

    def load(self) -> Maze:
        try:
            generator = MazeGenerator(
                size=(self.width, self.height),
                perfect=self.perfect,
                entry_cell=self.entry,
                exit_cell=self.exit,
                seed=self.seed,
            )
        except Exception as err:
            raise MazeGenerationError(f"Maze generation failed: {err}")

        return self._convert(generator)

    def _convert(self, generator: MazeGenerator) -> Maze:
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



if __name__ == "__main__":
    loader = MazeLoader(width=21, height=21, entry=(10, 10), exit=(20, 20), seed=42)
    maze = loader.load()
    print(maze.cells[0][0])
