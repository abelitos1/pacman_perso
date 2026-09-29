"""Pac-Man entry point: python3 pac-man.py [config.json]"""
import sys

from config.loader import ConfigError, load_config
from game.game_state import GameState
from game.maze_loader import MazeGenerationError
from ui.app import run

DEFAULT_CONFIG = "config.json"
CELL_SIZE = 40


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG
    try:
        config = load_config(path)
        state = GameState.new_game(config)
    except (ConfigError, MazeGenerationError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    run(state, CELL_SIZE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
