import json
from dataclasses import dataclass
from typing import Any
from config.loader import ConfigError


@dataclass
class LevelConfig:
    width: int
    height: int


@dataclass
class Config:
    highscore_filename: str
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
    levels: list[LevelConfig]


def read_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            out = ""
            for index, line in enumerate(f, start=1):
                clean_line = line.strip()
                if clean_line == "":
                    continue
                if clean_line.startswith("#"):
                    continue
                else:
                    out += clean_line + "\n"
    except OSError as e:
        raise ConfigError(f"cannot read {path}: {e}")

    return (out)


def parse_json(text: str) -> dict[str, Any]:
    out = {}
    try:
        out = json.loads(read_file(text))
    except json.JSONDecodeError as e:
        raise ConfigError(f"invalid JSON: {e.msg}\
 (line {e.lineno}, col {e.colno})") from e
    return (out)


def _get_int(data: dict[str, Any], key: str,  default: int, min_value: int = 0) -> int:

    value = data.get(key)
    if value is None:
        print(f"missing key '{key}', using default {default}")
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        print(f"invalid type for '{key}' (expected int), using default {default}")
        return default
    if value < min_value:
        print(f"'{key}' below minimum ({min_value}), using default {default}")
        return default
    return value


def _get_int(data: dict[str, Any], key: str, default: int, min_value: int = 0) -> str:

    value = data.get(key)
    if value is None:
        print(f"missing key '{key}', using default {default}")
        return default
    if not isinstance(value, str):
        print(f"invalid type for '{key}' (expected str), using default {default}")
        return default
    return value


def _get_levels(data: dict[str, Any]) -> list[LevelConfig]:
    raw_levels = data.get("level")

    if not isinstance(raw_levels, list) or len(raw_levels) == 0:
        print("missing/invalid 'level' array, using fallback of 10 levels 21x21")
        result = []
        for _ in range(10):
            result.append(LevelConfig(width=21, height=21))
        return result

    levels: list[LevelConfig] = []
    for index, entry in enumerate(raw_levels):
        if not isinstance(entry, dict):
            print(f"invalid level entry at index {index}, using fallback 21x21")
            levels.append(LevelConfig(width=21, height=21))
            continue

        width = _get_int(entry, "width", default=21, min_value=5)
        height = _get_int(entry, "height", default=21, min_value=5)
        levels.append(LevelConfig(width=width, height=height))

    return levels


def load_config(path: str) -> Config:
    if not path.endswith(".json"):
        raise ConfigError("config file must be a .json file")

    data = parse_json(read_file(path))

    if not isinstance(data, dict):
        raise ConfigError("config root must be a JSON object")
    
    return Config(
        highscore_filename = _get_str(data, "highscore_filename",default = "highscores.json"),
        lives = _get_int(data, "lives", default=3, min_value=0),
        pacgum = _get_int(data, "pacgum", default=42, min_value=0),
        points_per_pacgum = _get_int(data, "points_per_pacgum", default=10, min_value=0),
        points_per_super_pacgum = _get_int(data, "points_per_super_pacgum", default=50, min_value=0),
        points_per_ghost = _get_int(data, "points_per_ghost", default=200, min_value=0),
        seed = _get_int(data, "seed", default=42, min_value=0),
        level_max_time = _get_int(data, "level_max_time", default=90, min_value=1),
        levels = _get_levels(data),
    )
