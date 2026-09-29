"""Level building: maze generation and placement of everything in it."""
from collections import deque
from dataclasses import dataclass

from config.loader import Config
from game.entity import DIRECTIONS, can_step
from game.maze_loader import Coord, Maze, MazeLoader


@dataclass
class LevelLayout:
    """Where everything starts in a level.

    Attributes:
        maze: The generated maze.
        player_spawn: Open cell closest to the middle of the maze.
        ghost_homes: One cell per corner, where each ghost starts and
            respawns.
        pacgums: Cells holding a small pacgum (every reachable cell
            except the player spawn and the super-pacgums).
        super_pacgums: Cells holding a super-pacgum (the 4 corners).
    """

    maze: Maze
    player_spawn: Coord
    ghost_homes: list[Coord]
    pacgums: set[Coord]
    super_pacgums: set[Coord]


def build_level_maze(config: Config, level_index: int) -> Maze:
    """Generate the maze of a level.

    Level 1 uses the config seed, the following ones are random. If
    `level_index` is past the configured levels, the last one is reused.
    """
    if level_index >= len(config.levels):
        print("no more levels defined, reusing last level")
        level_index = len(config.levels) - 1
    level = config.levels[level_index]

    seed = config.seed if level_index == 0 else 0

    loader = MazeLoader(
        width=level.width,
        height=level.height,
        entry=(0, 0),
        exit=(level.width - 1, level.height - 1),
        seed=seed,
        perfect=False,
    )
    return loader.load()


def reachable_cells(maze: Maze, start: Coord) -> set[Coord]:
    """All cells reachable from `start` (breadth-first search).

    The isolated cells of the '42' pattern are never reachable, so
    nothing gets placed inside them.
    """
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for direction, (dx, dy) in DIRECTIONS.items():
            nxt = (x + dx, y + dy)
            if nxt not in seen and can_step(maze, x, y, direction):
                seen.add(nxt)
                queue.append(nxt)
    return seen


def nearest(cells: set[Coord], target: Coord) -> Coord:
    """Cell of `cells` closest to `target` (Manhattan distance).

    Ties are broken by position so the result is deterministic.
    """
    return min(cells, key=lambda c: (abs(c[0] - target[0])
                                     + abs(c[1] - target[1]), c))


def build_level(config: Config, level_index: int) -> LevelLayout:
    """Generate a level and place the player, ghosts and pacgums."""
    maze = build_level_maze(config, level_index)
    open_cells = reachable_cells(maze, maze.entry)
    w, h = maze.width, maze.height

    player_spawn = nearest(open_cells, (w // 2, h // 2))
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    homes = [nearest(open_cells, corner) for corner in corners]

    pacgums = open_cells - set(homes) - {player_spawn}

    return LevelLayout(
        maze=maze,
        player_spawn=player_spawn,
        ghost_homes=homes,
        pacgums=pacgums,
        super_pacgums=set(homes),
    )
