import json
from dataclasses import dataclass
from typing import Any, Optional

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
        raise ConfigError(f"invalid JSON: {e.msg} (line {e.lineno}, col {e.colno})") from e
    return (out)





if __name__ == "__main__":
    print(parse_json("config.json"))