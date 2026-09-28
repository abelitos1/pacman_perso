from config.loader import Config
from game.maze_loader import Maze, MazeLoader


def build_level_maze(config: Config, level_index: int) -> Maze:
    if level_index >= len(config.levels):
        print("no more levels defined, reusing last level")
        level_index = len(config.levels) - 1
    level = config.levels[level_index]

    if level_index == 0:
        seed = config.seed
    else:
        seed = 0

    loader = MazeLoader(
        width=level.width,
        height=level.height,
        entry=(0, 0),
        exit=(level.width - 1, level.height - 1),
        seed=seed,
        perfect=False,
    )

    return loader.load()
