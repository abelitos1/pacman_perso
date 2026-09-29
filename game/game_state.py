"""Rules of the game: score, lives, levels, timer, ghosts and cheats.

GameState knows nothing about display or keyboard: the UI calls
`update()` once per frame with the elapsed time and the direction asked
by the player, then draws what it finds in the state.
"""
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from config.loader import Config
from game.cheats import Cheat, CheatState
from game.ghost import Ghost
from game.level import LevelLayout, build_level
from game.maze_loader import Coord, Maze
from game.player import PLAYER_SPEED, Player

FRIGHTENED_DURATION = 7.0  # seconds ghosts stay edible
COLLISION_DISTANCE = 0.6  # in cells, between player and ghost centers
FIRST_RELEASE = 2.0  # seconds before the first ghost leaves its corner
RELEASE_INTERVAL = 3.0  # then one more ghost every RELEASE_INTERVAL
FAST_FACTOR = 2.0  # player speed multiplier of the FAST cheat

# (color, randomness): Blinky chases hard, Clyde is... weird.
GHOST_PERSONALITIES: list[tuple[tuple[int, int, int], float]] = [
    ((255, 0, 0), 0.1),      # Blinky
    ((255, 184, 255), 0.3),  # Pinky
    ((0, 255, 255), 0.5),    # Inky
    ((255, 184, 82), 0.7),   # Clyde
]


class Status(Enum):
    """Where the game is at."""

    PLAYING = "playing"
    GAME_OVER = "game_over"
    VICTORY = "victory"


@dataclass
class GameState:
    """Everything that makes up a running game, independent of display.

    Score, lives and cheats are kept from one level to the next.
    """

    config: Config
    level_index: int
    layout: LevelLayout
    player: Player
    ghosts: list[Ghost]
    score: int = 0
    time_left: float = 0.0
    frightened_time: float = 0.0
    paused: bool = False
    status: Status = Status.PLAYING
    pacgums: set[Coord] = field(default_factory=set)
    super_pacgums: set[Coord] = field(default_factory=set)
    cheats: CheatState = field(default_factory=CheatState)

    @classmethod
    def new_game(cls, config: Config) -> "GameState":
        """Start a game at level 1 with the configured number of lives.

        Raises:
            MazeGenerationError: If the maze of level 1 cannot be built.
        """
        layout = build_level(config, 0)
        state = cls(
            config=config,
            level_index=0,
            layout=layout,
            player=Player.at_cell(layout.player_spawn, lives=config.lives),
            ghosts=[],
        )
        state._enter_level(0, layout)
        return state

    # ------------------------------------------------------------------
    # Read-only views
    # ------------------------------------------------------------------

    @property
    def maze(self) -> Maze:
        """Shortcut to the current level's maze."""
        return self.layout.maze

    @property
    def level_count(self) -> int:
        """Number of levels to clear to win the game."""
        return len(self.config.levels)

    @property
    def is_over(self) -> bool:
        """True once the game is lost or won."""
        return self.status is not Status.PLAYING

    def toggle_pause(self) -> None:
        """Pause or resume the game (no effect once it is over)."""
        if not self.is_over:
            self.paused = not self.paused

    # ------------------------------------------------------------------
    # Levels and lives
    # ------------------------------------------------------------------

    def _enter_level(self, index: int, layout: LevelLayout) -> None:
        """Switch to level `index` and put everyone at their start."""
        self.layout = layout
        self.level_index = index
        self.pacgums = set(layout.pacgums)
        self.super_pacgums = set(layout.super_pacgums)
        self.ghosts = [
            Ghost.at_home(home, color, randomness)
            for home, (color, randomness)
            in zip(layout.ghost_homes, GHOST_PERSONALITIES)
        ]
        self.time_left = float(self.config.level_max_time)
        self._reset_positions()

    def _complete_level(self) -> None:
        """Go to the next level, or win if it was the last one."""
        index = self.level_index + 1
        if index >= self.level_count:
            self.status = Status.VICTORY
        else:
            self._enter_level(index, build_level(self.config, index))

    def _reset_positions(self) -> None:
        """Player back to the middle, ghosts back to their corners.

        The ghosts then come out one by one: the first after
        FIRST_RELEASE seconds, the next ones RELEASE_INTERVAL apart.
        """
        self.player.place_at(*self.layout.player_spawn)
        self.player.stop()
        for i, ghost in enumerate(self.ghosts):
            ghost.reset(FIRST_RELEASE + i * RELEASE_INTERVAL)
        self.frightened_time = 0.0

    def _lose_life(self) -> None:
        """Remove a life and restart the level timer; game over at 0."""
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.player.lives = 0
            self.status = Status.GAME_OVER
            return
        self._reset_positions()
        self.time_left = float(self.config.level_max_time)

    # ------------------------------------------------------------------
    # Pacgums and ghosts
    # ------------------------------------------------------------------

    def _frighten_ghosts(self) -> None:
        """Make every ghost edible for FRIGHTENED_DURATION seconds."""
        self.frightened_time = FRIGHTENED_DURATION
        for ghost in self.ghosts:
            ghost.set_edible(True)

    def _eat_pacgums(self) -> None:
        """Eat what lies in the player's current cell."""
        cell = self.player.nearest_cell
        if cell in self.pacgums:
            self.pacgums.remove(cell)
            self.score += self.config.points_per_pacgum
        elif cell in self.super_pacgums:
            self.super_pacgums.remove(cell)
            self.score += self.config.points_per_super_pacgum
            self._frighten_ghosts()

    def _touches(self, ghost: Ghost) -> bool:
        """True if the ghost and the player meet.

        Two tests are needed:
          1. their drawn centers are closer than COLLISION_DISTANCE;
          2. they swap cells during the same frame. With a large frame
             time they can cross each other between two frames without
             ever being close at a frame, so test 1 alone would miss it.
        """
        p, g = self.player, ghost
        if math.hypot(p.x - g.x, p.y - g.y) < COLLISION_DISTANCE:
            return True
        return ((p.cell_x, p.cell_y) == (g.target_x, g.target_y)
                and (g.cell_x, g.cell_y) == (p.target_x, p.target_y)
                and p.is_moving() and g.is_moving())

    def _handle_collisions(self) -> None:
        """Eat edible ghosts, or lose a life to a hunting one."""
        for ghost in self.ghosts:
            if ghost.is_eaten or not self._touches(ghost):
                continue
            if ghost.edible:
                ghost.get_eaten()
                self.score += self.config.points_per_ghost
            elif not self.cheats.invincible:
                self._lose_life()
                return

    def _update_frightened(self, dt: float) -> None:
        """Count down edible mode and turn it off when it runs out."""
        if self.frightened_time <= 0:
            return
        self.frightened_time = max(0.0, self.frightened_time - dt)
        if self.frightened_time == 0:
            for ghost in self.ghosts:
                ghost.set_edible(False)

    # ------------------------------------------------------------------
    # Cheat mode
    # ------------------------------------------------------------------

    def toggle_cheat_mode(self) -> None:
        """Switch cheat mode on or off (active cheats are kept)."""
        self.cheats.enabled = not self.cheats.enabled

    def use_cheat(self, cheat: Cheat) -> None:
        """Apply `cheat`; ignored unless cheat mode is on.

        Toggle cheats (INVINCIBLE, FREEZE_GHOSTS, FAST) flip on/off,
        the others act once.
        """
        if not self.cheats.enabled or self.is_over:
            return
        if cheat is Cheat.INVINCIBLE:
            self.cheats.invincible = not self.cheats.invincible
        elif cheat is Cheat.FREEZE_GHOSTS:
            self.cheats.ghosts_frozen = not self.cheats.ghosts_frozen
        elif cheat is Cheat.FAST:
            self.cheats.fast = not self.cheats.fast
        elif cheat is Cheat.EXTRA_LIFE:
            self.player.lives += 1
        elif cheat is Cheat.FRIGHTEN:
            self._frighten_ghosts()
        elif cheat is Cheat.SKIP_LEVEL:
            self._complete_level()

    # ------------------------------------------------------------------
    # Main update
    # ------------------------------------------------------------------

    def update(self, dt: float, direction: Optional[str]) -> None:
        """Advance the game by `dt` seconds.

        Order of one frame: move the player, eat, move the ghosts,
        resolve collisions, then check level end and the timer.

        Args:
            dt: Elapsed time in seconds.
            direction: Direction asked by the player this frame, if any.
        """
        if self.paused or self.is_over:
            return

        fast = FAST_FACTOR if self.cheats.fast else 1.0
        self.player.speed = PLAYER_SPEED * fast
        if direction is not None:
            self.player.steer(direction)
        self.player.update_in(self.maze, dt)
        self._eat_pacgums()

        if not self.cheats.ghosts_frozen:
            target = self.player.nearest_cell
            for ghost in self.ghosts:
                ghost.update_in(self.maze, dt, target)
        self._handle_collisions()
        if self.is_over:
            return
        self._update_frightened(dt)

        if not self.pacgums and not self.super_pacgums:
            self._complete_level()
            return

        self.time_left = max(0.0, self.time_left - dt)
        if self.time_left == 0:
            self._lose_life()
