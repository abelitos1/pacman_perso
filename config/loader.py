"""Config file loading: JSON with '#' comment lines.

Nothing in the file is mandatory: every missing or invalid value is
replaced by a safe default and reported with a message, unknown keys are
ignored. Only an unreadable file or invalid JSON stops the program.
"""
import json
from dataclasses import dataclass
from typing import Any, Optional

MAX_LEVEL_SIZE = 100
DEFAULT_LEVEL_SIZE = 21
FALLBACK_LEVEL_COUNT = 10


class ConfigError(Exception):
    """Raised when the config file cannot be used at all."""


@dataclass
class LevelConfig:
    """Size of one level's maze, in cells."""

    width: int
    height: int


@dataclass
class Config:
    """Validated game settings (see README, Configuration)."""

    highscore_filename: str
    lives: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
    levels: list[LevelConfig]


def read_file(path: str) -> str:
    """Read the config file, turning '#' comment lines into blank lines."""
    try:
        with open(path, "r") as f:
            out = ""
            for line in f:
                # comments become blank lines, so JSON error line
                # numbers still match the file
                if line.strip().startswith("#"):
                    out += "\n"
                else:
                    out += line
    except OSError as e:
        raise ConfigError(f"cannot read {path}: {e}") from e
    return out


def parse_json(text: str) -> dict[str, Any]:
    """Parse the JSON text; the root must be an object."""
    try:
        out = json.loads(text)
    except json.JSONDecodeError as e:
        raise ConfigError(f"invalid JSON: {e.msg} "
                          f"(line {e.lineno}, col {e.colno})") from e
    if not isinstance(out, dict):
        raise ConfigError("config root must be a JSON object")
    return out


def _get_int(data: dict[str, Any], key: str, default: int,
             min_value: int = 0, max_value: Optional[int] = None) -> int:
    """Read an int, falling back to `default` if missing or invalid.

    Values above `max_value` are clamped to it.
    """
    value = data.get(key)
    if value is None:
        print(f"missing key '{key}', using default {default}")
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        print(f"invalid type for '{key}' (expected int), "
              f"using default {default}")
        return default
    if value < min_value:
        print(f"'{key}' below minimum ({min_value}), using default {default}")
        return default
    if max_value is not None and value > max_value:
        print(f"'{key}' above maximum ({max_value}), clamped to {max_value}")
        return max_value
    return value


def _get_str(data: dict[str, Any], key: str, default: str) -> str:
    """Read a string, falling back to `default` if missing or invalid."""
    value = data.get(key)
    if value is None:
        print(f"missing key '{key}', using default {default}")
        return default
    if not isinstance(value, str):
        print(f"invalid type for '{key}' (expected str), "
              f"using default {default}")
        return default
    return value


def _get_levels(data: dict[str, Any]) -> list[LevelConfig]:
    """Read the 'level' array of {"width", "height"} objects.

    A missing or empty array gives FALLBACK_LEVEL_COUNT default levels;
    an invalid entry gives one default level.
    """
    size = DEFAULT_LEVEL_SIZE
    raw_levels = data.get("level")
    if not isinstance(raw_levels, list) or len(raw_levels) == 0:
        print(f"missing/invalid 'level' array, using fallback of "
              f"{FALLBACK_LEVEL_COUNT} levels {size}x{size}")
        return [LevelConfig(size, size) for _ in range(FALLBACK_LEVEL_COUNT)]

    levels: list[LevelConfig] = []
    for index, entry in enumerate(raw_levels):
        if not isinstance(entry, dict):
            print(f"invalid level entry at index {index}, "
                  f"using fallback {size}x{size}")
            levels.append(LevelConfig(size, size))
            continue
        width = _get_int(entry, "width", default=size, min_value=5,
                         max_value=MAX_LEVEL_SIZE)
        height = _get_int(entry, "height", default=size, min_value=5,
                          max_value=MAX_LEVEL_SIZE)
        levels.append(LevelConfig(width=width, height=height))
    return levels


def load_config(path: str) -> Config:
    """Load and validate a config file.

    Missing or invalid values are replaced by defaults with a message;
    unknown keys are ignored.

    Raises:
        ConfigError: If the file is not a readable JSON object.
    """
    if not path.endswith(".json"):
        raise ConfigError("config file must be a .json file")

    data = parse_json(read_file(path))

    return Config(
        highscore_filename=_get_str(data, "highscore_filename",
                                    default="highscores.json"),
        lives=_get_int(data, "lives", default=3, min_value=1),
        points_per_pacgum=_get_int(data, "points_per_pacgum",
                                   default=10, min_value=0),
        points_per_super_pacgum=_get_int(data, "points_per_super_pacgum",
                                         default=50, min_value=0),
        points_per_ghost=_get_int(data, "points_per_ghost", default=200,
                                  min_value=0),
        seed=_get_int(data, "seed", default=42, min_value=0),
        level_max_time=_get_int(data, "level_max_time", default=90,
                                min_value=1),
        levels=_get_levels(data),
    )
