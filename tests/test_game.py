"""Tests of the game rules: movement, eating, ghosts, lives, cheats."""
import unittest

from config.loader import load_config
from game.cheats import Cheat
from game.entity import can_step
from game.game_state import FIRST_RELEASE, GameState, Status
from game.ghost import RESPAWN_DELAY


class GameRulesTest(unittest.TestCase):
    """Rules implemented by GameState, without any display."""

    def setUp(self) -> None:
        """Start a new game on the project config."""
        self.config = load_config("config.json")
        self.state = GameState.new_game(self.config)
        self.player = self.state.player

    def run_frames(self, frames: int, dt: float = 0.01) -> None:
        """Advance the game `frames` times with no key pressed."""
        for _ in range(frames):
            self.state.update(dt, None)

    def test_one_key_press_keeps_pacman_moving(self) -> None:
        """Arcade controls: a tap is enough, Pac-Man keeps going."""
        self.state.ghosts = []
        x, y = self.state.layout.player_spawn
        direction = next(d for d in ("UP", "DOWN", "LEFT", "RIGHT")
                         if can_step(self.state.maze, x, y, d))
        self.state.update(0.01, direction)
        self.run_frames(20)
        self.assertNotEqual(self.player.nearest_cell, (x, y))

    def test_eating_scores_points(self) -> None:
        """Pacgums and super-pacgums give their configured points."""
        gum = next(iter(self.state.pacgums))
        self.player.place_at(*gum)
        self.state.update(0.0, None)
        self.assertEqual(self.state.score, self.config.points_per_pacgum)
        self.assertNotIn(gum, self.state.pacgums)

    def test_super_pacgum_makes_ghosts_edible(self) -> None:
        """An edible ghost can be eaten and respawns later."""
        for ghost in self.state.ghosts:  # away from the super-pacgum
            ghost.place_at(*self.state.layout.player_spawn)
        self.player.place_at(*self.state.layout.ghost_homes[0])
        self.state.update(0.0, None)
        self.assertTrue(all(g.edible for g in self.state.ghosts))
        ghost = self.state.ghosts[1]
        ghost.place_at(*self.player.nearest_cell)
        self.state.update(0.0, None)
        self.assertTrue(ghost.is_eaten)
        ghost.update_in(self.state.maze, RESPAWN_DELAY + 0.1, (0, 0))
        self.assertFalse(ghost.is_eaten)

    def test_ghost_costs_a_life_then_game_over(self) -> None:
        """Each hunting-ghost contact costs a life; 0 lives ends it."""
        for lives_left in range(self.config.lives - 1, -1, -1):
            ghost = self.state.ghosts[0]
            ghost.place_at(*self.player.nearest_cell)
            self.state.update(0.0, None)
            self.assertEqual(self.player.lives, lives_left)
        self.assertIs(self.state.status, Status.GAME_OVER)

    def test_ghosts_leave_their_corner_one_by_one(self) -> None:
        """Only the first ghost moves just after FIRST_RELEASE."""
        self.state.cheats.invincible = True
        self.run_frames(int(FIRST_RELEASE * 100) + 20)
        moving = [g.is_moving() for g in self.state.ghosts]
        self.assertEqual(moving, [True, False, False, False])

    def test_timer_running_out_costs_a_life(self) -> None:
        """At 0 seconds a life is lost and the timer restarts."""
        self.state.ghosts = []
        self.state.time_left = 0.005
        self.state.update(0.01, None)
        self.assertEqual(self.player.lives, self.config.lives - 1)
        self.assertEqual(self.state.time_left, self.config.level_max_time)

    def test_clearing_all_levels_wins(self) -> None:
        """Score and lives are kept between levels up to the victory."""
        for _ in range(len(self.config.levels)):
            self.state.ghosts = []
            self.state.pacgums.clear()
            self.state.super_pacgums.clear()
            self.state.update(0.0, None)
        self.assertIs(self.state.status, Status.VICTORY)
        self.assertEqual(self.player.lives, self.config.lives)

    def test_pause_freezes_the_game(self) -> None:
        """Nothing moves and the timer stops while paused."""
        self.state.toggle_pause()
        time_left = self.state.time_left
        self.run_frames(100)
        self.assertEqual(self.state.time_left, time_left)

    def test_cheats_need_cheat_mode(self) -> None:
        """Cheats do nothing until cheat mode is switched on."""
        self.state.use_cheat(Cheat.EXTRA_LIFE)
        self.assertEqual(self.player.lives, self.config.lives)
        self.state.toggle_cheat_mode()
        self.state.use_cheat(Cheat.EXTRA_LIFE)
        self.assertEqual(self.player.lives, self.config.lives + 1)

    def test_invincible_and_skip_level(self) -> None:
        """Invincibility ignores ghosts; skip level keeps the score."""
        self.state.toggle_cheat_mode()
        self.state.use_cheat(Cheat.INVINCIBLE)
        self.state.ghosts[0].place_at(*self.player.nearest_cell)
        self.state.update(0.0, None)
        self.assertEqual(self.player.lives, self.config.lives)
        self.state.use_cheat(Cheat.SKIP_LEVEL)
        self.assertEqual(self.state.level_index, 1)

    def test_freeze_ghosts(self) -> None:
        """Frozen ghosts do not move."""
        self.state.toggle_cheat_mode()
        self.state.use_cheat(Cheat.FREEZE_GHOSTS)
        before = [(g.x, g.y) for g in self.state.ghosts]
        self.state.cheats.invincible = True
        self.run_frames(1000)
        self.assertEqual(before, [(g.x, g.y) for g in self.state.ghosts])


if __name__ == "__main__":
    unittest.main()
