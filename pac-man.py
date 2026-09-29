"""Pac-Man entry point: python3 pac-man.py config.json"""
import sys

from config.loader import ConfigError, load_config
from game.maze_loader import MazeGenerationError
from highscore.manager import HighscoreManager

CELL_SIZE = 80  # preferred; reduced if the maze would not fit on screen
USAGE = "usage: python3 pac-man.py <config.json>"


def main(argv: list[str]) -> int:
    """Load the config and highscores, then open the main menu.

    Args:
        argv: Command line arguments, without the program name.

    Returns:
        Process exit code: 0 on success, 1 on error.
    """
    if len(argv) != 1:
        print(f"Error: expected exactly one argument.\n{USAGE}",
              file=sys.stderr)
        return 1
    try:
        config = load_config(argv[0])
        highscores = HighscoreManager(config.highscore_filename)
        highscores.load()
        # imported here so config errors are reported even without pygame
        from ui.app import App
        App(config, highscores, CELL_SIZE).run()
    except (ConfigError, MazeGenerationError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    except ImportError as err:
        print(f"Error: missing dependency ({err.name}), run 'make install'",
              file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 1
    except Exception as err:
        print(f"Unexpected error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
