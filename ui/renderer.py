import math
import sys
import time

import pygame

from config.loader import load_config
from game.game_state import build_level_maze
from game.maze_loader import Maze

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
SCALE = 2

NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3


class VisualState():
    bend: float
    bend_speed: float
    thick_l: float
    thick_u: float
    scale: int
    thick_speed: float
    fade: float
    chaos: bool


def preset_sober(stat: VisualState) -> None:
    stat.bend = 0
    stat.bend_speed = 0.05
    stat.thick_l = 5
    stat.thick_u = 5
    stat.thick_speed = 0.2
    stat.fade = 100


def preset_200ug(stat: VisualState) -> None:
    stat.bend = 0
    stat.bend_speed = 0.05
    stat.thick_l = 2
    stat.thick_u = 15
    stat.thick_speed = 0.2
    stat.fade = 18


def preset_500ug(stat: VisualState) -> None:
    stat.bend = 1
    stat.bend_speed = 0.1
    stat.thick_l = 2
    stat.thick_u = 16
    stat.thick_speed = 0.3
    stat.fade = 10


HORIZONTAL, VERTICAL = 0, 1

def _wall_phase(x: int, y: int, direction: int, chaos: bool, salt: float = 0.0) -> float:
    if chaos:
        return _phase(x, y, direction, salt)
    group = HORIZONTAL if direction in (NORTH, SOUTH) else VERTICAL
    return _phase(0, 0, group, salt)


def blblbl(rgb, u) -> int:
    if u == True:
        return (rgb + 1)
    else:
        return (rgb - 1)


def ahahahah(rgb, u) -> bool:
    if rgb == 150:
        return False
    elif rgb == 0:
        return True
    else:
        return u


def _phase(x: int, y: int, direction: int, salt: float = 0.0) -> float:
    """Deterministic pseudo-random phase in [0, 2*pi) for a given wall.

    Same (x, y, direction, salt) always returns the same phase, but two
    different walls get uncorrelated phases — that's what makes each bar
    pulse on its own rhythm instead of all moving in sync.
    """
    n = math.sin(x * 12.9898 + y * 78.233 + direction * 37.719 + salt) * 43758.5453
    return (n - math.floor(n)) * 2 * math.pi


def draw_maze(screen, maze, cell_size, stats: VisualState, elapsed: float, scale: int) -> None:
    thick_center = (stats.thick_u + stats.thick_l) / 2 * scale
    thick_range = (stats.thick_u - stats.thick_l) / 2 * scale
    bend_amp = stats.bend * scale
    speed_scale = 20

    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.cells[y][x]
            px, py = x * cell_size, y * cell_size

            if cell.wall_north:
                n = thick_center + thick_range * math.sin(elapsed * stats.thick_speed  * speed_scale+ _wall_phase(x, y, NORTH, stats.chaos))
                u = bend_amp * math.sin(elapsed * stats.bend_speed * speed_scale + _wall_phase(x, y, NORTH, stats.chaos,salt=99))
                pygame.draw.line(screen, WHITE, (px, py - u), (px + cell_size, py + u), int(n))
            if cell.wall_west:
                n = thick_center + thick_range * math.sin(elapsed * stats.thick_speed  * speed_scale+ _wall_phase(x, y, WEST, stats.chaos))
                u = bend_amp * math.sin(elapsed * stats.bend_speed * speed_scale + _wall_phase(x, y, WEST, stats.chaos,salt=99))
                pygame.draw.line(screen, WHITE, (px + u, py), (px - u, py + cell_size), int(n))
            if cell.wall_south:
                n = thick_center + thick_range * math.sin(elapsed * stats.thick_speed  * speed_scale+ _wall_phase(x, y, SOUTH, stats.chaos))
                u = bend_amp * math.sin(elapsed * stats.bend_speed * speed_scale + _wall_phase(x, y, SOUTH, stats.chaos,salt=99))
                pygame.draw.line(screen, WHITE, (px, py + cell_size - u), (px + cell_size, py + cell_size + u), int(n))
            if cell.wall_east:
                n = thick_center + thick_range * math.sin(elapsed * stats.thick_speed  * speed_scale+ _wall_phase(x, y, EAST, stats.chaos))
                u = bend_amp * math.sin(elapsed * stats.bend_speed * speed_scale + _wall_phase(x, y, EAST, stats.chaos,salt=99))
                pygame.draw.line(screen, WHITE, (px + cell_size + u, py), (px + cell_size - u, py + cell_size), int(n))


def run_window(maze: Maze, cell_size: int) -> None:
    pygame.init()
    width = maze.width * cell_size
    height = maze.height * cell_size
    screen = pygame.display.set_mode((width, height))
    stats = VisualState()
    stats.chaos = False
    preset_sober(stats)
    running = True

    render_surface = pygame.Surface((width * SCALE, height * SCALE))
    render_surface.fill((0, 0, 0))

    fade = pygame.Surface((width * SCALE, height * SCALE))

    r = 150
    g = 75
    b = 0
    ru = False
    gu = True
    bu = True

    start_time = time.time()

    while running:
        fade.set_alpha(stats.fade)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP1:
                preset_sober(stats)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP2:
                preset_200ug(stats)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP3:
                preset_500ug(stats)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP4:
                stats.chaos = not stats.chaos

        r = blblbl(r, ru)
        g = blblbl(g, gu)
        b = blblbl(b, bu)
        ru = ahahahah(r, ru)
        gu = ahahahah(g, gu)
        bu = ahahahah(b, bu)

        time.sleep(0.010)

        fade.fill((r, g, b))
        render_surface.blit(fade, (0, 0))

        elapsed = time.time() - start_time
        draw_maze(render_surface, maze, cell_size * SCALE, stats, elapsed, SCALE)

        pygame.draw.rect(
            render_surface,
            WHITE,
            (0, 0, width * SCALE, height * SCALE),
            7 * SCALE,
        )

        scaled = pygame.transform.smoothscale(render_surface, (width, height))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    config = load_config("config.json")
    maze = build_level_maze(config, level_index=0)
    run_window(maze, 40)