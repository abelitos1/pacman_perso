"""Tests of the highscore table: validation, ranking, broken files."""
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

from highscore.manager import MAX_ENTRIES, HighscoreManager, clean_name


class HighscoreTest(unittest.TestCase):
    """HighscoreManager keeps a valid top 10 whatever the file holds."""

    def setUp(self) -> None:
        """Use a fresh temporary file for each test."""
        fd, self.path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.path)
        self.addCleanup(self.remove_file)

    def remove_file(self) -> None:
        """Delete the temporary file if a test created it."""
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_names_are_cleaned(self) -> None:
        """Only letters, digits and spaces, 10 characters at most."""
        self.assertEqual(clean_name("  Bob!42  "), "Bob42")
        self.assertEqual(clean_name("abcdefghijklmnop"), "abcdefghij")
        self.assertEqual(clean_name("!!!"), "")

    def test_top_ten_is_kept_sorted(self) -> None:
        """Best first, only MAX_ENTRIES kept, saved and reloaded."""
        table = HighscoreManager(self.path)
        for score in range(1, 15):
            table.add(f"p{score}", score * 10)
        self.assertEqual(len(table.entries), MAX_ENTRIES)
        self.assertEqual(table.entries[0].score, 140)
        self.assertTrue(table.save())
        reloaded = HighscoreManager(self.path)
        reloaded.load()
        self.assertEqual(reloaded.entries, table.entries)

    def test_missing_or_broken_file_gives_empty_table(self) -> None:
        """A missing file or invalid JSON never raises."""
        table = HighscoreManager(self.path)
        table.load()
        self.assertEqual(table.entries, [])
        with open(self.path, "w") as f:
            f.write("{not json")
        with redirect_stdout(StringIO()):
            table.load()
        self.assertEqual(table.entries, [])

    def test_invalid_entries_are_skipped(self) -> None:
        """Bad names and negative scores are dropped one by one."""
        with open(self.path, "w") as f:
            json.dump([{"name": "ok", "score": 5},
                       {"name": "!!", "score": 9},
                       {"name": "neg", "score": -1}, "junk"], f)
        table = HighscoreManager(self.path)
        with redirect_stdout(StringIO()):
            table.load()
        self.assertEqual([e.name for e in table.entries], ["ok"])


if __name__ == "__main__":
    unittest.main()
