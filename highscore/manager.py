"""Persistent top 10 highscores, stored in a JSON file."""
import json
from dataclasses import dataclass
from typing import Any, Optional

MAX_ENTRIES = 10
NAME_MAX_LENGTH = 10


@dataclass
class HighscoreEntry:
    """One line of the highscore table."""

    name: str
    score: int


def is_valid_name_char(char: str) -> bool:
    """True for ASCII letters, digits and spaces."""
    if len(char) != 1 or not char.isascii():
        return False
    return char.isalnum() or char == " "


def clean_name(name: str) -> str:
    """Keep only allowed characters, max NAME_MAX_LENGTH, no outer spaces.

    Returns:
        The cleaned name ("" if nothing valid is left).
    """
    kept = "".join(c for c in name if is_valid_name_char(c))
    return kept.strip()[:NAME_MAX_LENGTH].strip()


class HighscoreManager:
    """Loads, updates and saves the highscores.

    The file is a JSON list of {"name": str, "score": int}. A missing or
    broken file never crashes the game: it is reported and the table
    starts empty; invalid entries are skipped one by one.
    """

    def __init__(self, path: str) -> None:
        """Remember where the highscores live (nothing is read yet)."""
        self.path = path
        self.entries: list[HighscoreEntry] = []

    def load(self) -> None:
        """Read the file, keeping the valid entries (top 10)."""
        self.entries = []
        try:
            with open(self.path, "r") as f:
                data: Any = json.load(f)
        except FileNotFoundError:
            return
        except (OSError, json.JSONDecodeError) as err:
            print(f"highscores: cannot read {self.path} ({err}), "
                  "starting with an empty table")
            return
        if not isinstance(data, list):
            print(f"highscores: {self.path} is not a list, ignored")
            return
        for item in data:
            entry = self._parse_entry(item)
            if entry is None:
                print(f"highscores: invalid entry {item!r} skipped")
            else:
                self.entries.append(entry)
        self._sort()

    @staticmethod
    def _parse_entry(item: Any) -> Optional[HighscoreEntry]:
        """Build an entry from JSON data, or None if it is invalid."""
        if not isinstance(item, dict):
            return None
        name, score = item.get("name"), item.get("score")
        if not isinstance(name, str) or not clean_name(name):
            return None
        if (not isinstance(score, int) or isinstance(score, bool)
                or score < 0):
            return None
        return HighscoreEntry(clean_name(name), score)

    def _sort(self) -> None:
        """Best scores first, keep only the top MAX_ENTRIES."""
        self.entries.sort(key=lambda e: -e.score)
        del self.entries[MAX_ENTRIES:]

    def qualifies(self, score: int) -> bool:
        """True if `score` would enter the table."""
        if score <= 0:
            return False
        if len(self.entries) < MAX_ENTRIES:
            return True
        return score > self.entries[-1].score

    def add(self, name: str, score: int) -> bool:
        """Insert a score if the name is valid and the score qualifies.

        Returns:
            True if the entry was added.
        """
        name = clean_name(name)
        if not name or not self.qualifies(score):
            return False
        self.entries.append(HighscoreEntry(name, score))
        self._sort()
        return True

    def save(self) -> bool:
        """Write the table to disk.

        Returns:
            False (after printing why) if the file could not be written.
        """
        data = [{"name": e.name, "score": e.score} for e in self.entries]
        try:
            with open(self.path, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as err:
            print(f"highscores: cannot save to {self.path} ({err})")
            return False
        return True
