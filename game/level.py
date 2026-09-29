from config.loader import Config
from game.maze_loader import Maze, MazeLoader


def build_level_maze(config: Config, level_index: int) -> Maze:
    """Generate the maze of a level. Level 1 uses the config seed, the
    following ones are random."""
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
