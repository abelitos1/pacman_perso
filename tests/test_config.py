"""Tests of the config loader: comments, defaults, clamping, errors."""
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

from config.loader import (FALLBACK_LEVEL_COUNT, MAX_LEVEL_SIZE, Config,
                           ConfigError, load_config)


def write_temp(content: str, suffix: str = ".json") -> str:
    """Write `content` to a temporary file and return its path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class ConfigLoaderTest(unittest.TestCase):
    """load_config() never crashes on bad values and reports them."""

    def load(self, content: str) -> tuple[Config, str]:
        """Load `content` as a config, returning it and what was printed."""
        path = write_temp(content)
        self.addCleanup(os.remove, path)
        out = StringIO()
        with redirect_stdout(out):
            config = load_config(path)
        return config, out.getvalue()

    def test_project_config_is_valid(self) -> None:
        """The shipped config.json loads with at least 10 levels."""
        config = load_config("config.json")
        self.assertGreaterEqual(len(config.levels), 10)

    def test_comments_are_ignored(self) -> None:
        """Lines starting with '#' are comments."""
        config, _ = self.load('# comment\n{\n  # another\n  "lives": 5\n}\n')
        self.assertEqual(config.lives, 5)

    def test_missing_keys_use_defaults(self) -> None:
        """An empty object gives a playable config and messages."""
        config, out = self.load("{}")
        self.assertEqual(config.lives, 3)
        self.assertEqual(len(config.levels), FALLBACK_LEVEL_COUNT)
        self.assertIn("missing key", out)

    def test_invalid_values_are_replaced_or_clamped(self) -> None:
        """Wrong types fall back to defaults, huge sizes are clamped."""
        config, out = self.load(
            '{"lives": "x", "level": [{"width": 999, "height": 2}],'
            ' "unknown": 1}')
        self.assertEqual(config.lives, 3)
        level = config.levels[0]
        self.assertEqual(level.width, MAX_LEVEL_SIZE)
        self.assertEqual(level.height, 21)
        self.assertIn("invalid type", out)

    def test_unusable_files_raise_config_error(self) -> None:
        """Missing file, wrong extension and broken JSON are errors."""
        with self.assertRaises(ConfigError):
            load_config("does_not_exist.json")
        with self.assertRaises(ConfigError):
            load_config("Makefile")
        path = write_temp('{"lives": 3,,}')
        self.addCleanup(os.remove, path)
        with self.assertRaises(ConfigError):
            load_config(path)


if __name__ == "__main__":
    unittest.main()
