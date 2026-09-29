"""Draws a GameState to the window, one frame at a time."""
import time

import pygame

from game.game_state import GameState
from game.maze_loader import Maze
from ui.effects import (ColorCycle, VisualState, make_star_layers,
                        preset_200ug, preset_500ug, preset_sober)
from ui.hud import HUD_HEIGHT, Hud
from ui.maze_view import WALL_COLOR, draw_maze
from ui.sprites import draw_ghost, draw_pacgums, draw_player

BASE_CELL_SIZE = 40  # wall thickness presets are tuned for this size
MIN_CELL_SIZE = 8
SCREEN_MARGIN = 0.9  # use at most 90% of the screen
FALLBACK_SCREEN = (1280, 800)
BORDER_WIDTH = 7
FLASH_BELOW = 2.0  # edible ghosts flash during their last seconds


def desktop_size() -> tuple[int, int]:
    """Size of the screen in pixels (FALLBACK_SCREEN if unknown).

    Unlike display.Info(), this stays right once a window is open.
    """
    try:
        sizes = pygame.display.get_desktop_sizes()
    except pygame.error:
        return FALLBACK_SCREEN
    if not sizes or sizes[0][0] <= 0 or sizes[0][1] <= 0:
        return FALLBACK_SCREEN
    width, height = sizes[0]
    return width, height


def fit_cell_size(maze: Maze, screen: tuple[int, int],
                  max_cell: int = BASE_CELL_SIZE) -> int:
    """Largest cell size (up to `max_cell`) fitting maze + HUD on screen.

    Args:
        maze: Maze to display.
        screen: Desktop size in pixels.
        max_cell: Preferred cell size, used when the maze is small.

    Returns:
        Cell size in pixels, never below MIN_CELL_SIZE.
    """
    avail_w = screen[0] * SCREEN_MARGIN
    avail_h = screen[1] * SCREEN_MARGIN - HUD_HEIGHT
    size = int(min(avail_w / maze.width, avail_h / maze.height, max_cell))
    return max(MIN_CELL_SIZE, size)


class Renderer:
    """Owns the window and draws the maze, sprites, HUD and effects."""

    def __init__(self, state: GameState, max_cell_size: int,
                 desktop: tuple[int, int]) -> None:
        """Open the window sized for the first level.

        Args:
            state: The game to draw.
            max_cell_size: Preferred cell size in pixels.
            desktop: Screen size in pixels, the window fits inside.
        """
        self.desktop = desktop
        self.max_cell_size = max_cell_size
        self.visual = VisualState()
        self.colors = ColorCycle()
        self.hud = Hud()
        self.start_time = time.time()
        self.level_index = -1
        self.setup_level(state)

    def setup_level(self, state: GameState) -> None:
        """(Re)build the window and surfaces for the current level."""
        maze = state.maze
        self.level_index = state.level_index
        self.cell_size = fit_cell_size(maze, self.desktop,
                                       self.max_cell_size)
        self.scale = self.cell_size / BASE_CELL_SIZE
        self.width = maze.width * self.cell_size
        self.height = maze.height * self.cell_size
        self.screen = pygame.display.set_mode(
            (self.width, self.height + HUD_HEIGHT))
        pygame.display.set_caption(f"Pac-Man - level {state.level_index + 1}")

        size = (self.width, self.height)
        self.render_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.render_surface.fill((0, 0, 0))
        self.fade = pygame.Surface(size)
        self.star_layers = make_star_layers(self.width, self.height)

    def handle_key(self, key: int) -> None:
        """Visual effect shortcuts: u/i/o presets, p toggles chaos."""
        if key == pygame.K_u:
            preset_sober(self.visual)
        elif key == pygame.K_i:
            preset_200ug(self.visual)
        elif key == pygame.K_o:
            preset_500ug(self.visual)
        elif key == pygame.K_p:
            self.visual.chaos = not self.visual.chaos

    def draw(self, state: GameState) -> None:
        """Draw one full frame (the caller flips the display)."""
        if state.level_index != self.level_index:
            self.setup_level(state)
        surface = self.render_surface
        cell = self.cell_size

        self.fade.set_alpha(int(self.visual.fade))
        self.fade.fill(self.colors.step())
        surface.blit(self.fade, (0, 0))
        for layer in self.star_layers:
            layer.draw(surface)

        elapsed = time.time() - self.start_time
        draw_maze(surface, state.maze, cell, self.visual, elapsed,
                  self.scale)
        draw_pacgums(surface, state.pacgums, state.super_pacgums, cell,
                     elapsed)
        draw_player(surface, state.player, cell, elapsed)
        flash = (0 < state.frightened_time < FLASH_BELOW
                 and int(elapsed * 6) % 2 == 0)
        for ghost in state.ghosts:
            draw_ghost(surface, ghost, cell, flash)

        pygame.draw.rect(surface, WALL_COLOR, (0, 0, self.width, self.height),
                         max(1, int(BORDER_WIDTH * self.scale)))

        self.screen.blit(surface, (0, 0))
        self.hud.draw_bar(self.screen, state, self.height)
        self.hud.draw_cheats(self.screen, state)
