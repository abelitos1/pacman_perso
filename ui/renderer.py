"""Draws a GameState to the window, one frame at a time."""
import time

import pygame

from game.game_state import GameState
from ui.effects import (ColorCycle, VisualState, make_star_layers,
                        preset_200ug, preset_500ug, preset_sober)
from ui.maze_view import WALL_COLOR, draw_maze
from ui.sprites import draw_ghost, draw_player

SCALE = 1
BORDER_WIDTH = 7


class Renderer:

    def __init__(self, state: GameState, cell_size: int) -> None:
        self.cell_size = cell_size
        self.width = state.maze.width * cell_size
        self.height = state.maze.height * cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))

        size = (self.width * SCALE, self.height * SCALE)
        self.render_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.render_surface.fill((0, 0, 0))
        self.fade = pygame.Surface(size)

        self.visual = VisualState()
        self.colors = ColorCycle()
        self.star_layers = make_star_layers(size[0], size[1], SCALE)
        self.start_time = time.time()

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
        surface = self.render_surface
        cell = self.cell_size * SCALE

        self.fade.set_alpha(int(self.visual.fade))
        self.fade.fill(self.colors.step())
        surface.blit(self.fade, (0, 0))
        for layer in self.star_layers:
            layer.draw(surface)

        elapsed = time.time() - self.start_time
        draw_maze(surface, state.maze, cell, self.visual, elapsed, SCALE)
        draw_player(surface, state.player, cell)
        for ghost in state.ghosts:
            draw_ghost(surface, ghost, cell)

        pygame.draw.rect(surface, WALL_COLOR,
                         (0, 0, self.width * SCALE, self.height * SCALE),
                         BORDER_WIDTH * SCALE)

        scaled = pygame.transform.smoothscale(surface,
                                              (self.width, self.height))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()
