import math
import sys
import time
import random
import pygame
from game.player import Player
from config.loader import load_config
from game.game_state import build_level_maze
from game.maze_loader import Maze
PLAYER_COLOR = (255, 255, 0)

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
SCALE = 1

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


STAR_LAYERS = [
    {"count": 80, "radius": 0.5, "speed": -0.3, "alpha": 60},   # fond, petites, lentes
    {"count": 50, "radius": 1, "speed": -0.8, "alpha": 110},  # milieu
    {"count": 25, "radius": 2, "speed": -1.6, "alpha": 170},  # avant, plus grosses, rapides
]


def init_stars(count: int, width: int, height: int) -> list[dict]:
    return [
        {"x": random.uniform(0, width), "y": random.uniform(0, height)}
        for _ in range(count)
    ]


def draw_stars(surface, stars, speed: float, width: int, radius: int, alpha: int) -> None:
    for star in stars:
        star["x"] = (star["x"] + speed) % width
        pygame.draw.circle(
            surface,
            (255, 255, 255, alpha),
            (int(star["x"]), int(star["y"])),
            radius,
        )


def draw_player(surface, player: Player, cell_size: int) -> None:
    center = (
        int(player.x * cell_size + cell_size / 2),
        int(player.y * cell_size + cell_size / 2),
    )
    radius = int(cell_size / 2 * 0.6)
    pygame.draw.circle(surface, PLAYER_COLOR, center, radius)


def preset_sober(stat: VisualState) -> None:
    stat.bend = 0
    stat.bend_speed = 0.05
    stat.thick_l = 7
    stat.thick_u = 7
    stat.thick_speed = 0.2
    stat.fade = 100


def preset_200ug(stat: VisualState) -> None:
    stat.bend = 0
    stat.bend_speed = 0.05
    stat.thick_l = 2
    stat.thick_u = 15
    stat.thick_speed = 0.2
    stat.fade = 22


def preset_500ug(stat: VisualState) -> None:
    stat.bend = 1
    stat.bend_speed = 0.1
    stat.thick_l = 2
    stat.thick_u = 17
    stat.thick_speed = 0.25
    stat.fade = 15


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
    player = Player.at_center(maze)
    running = True

    render_surface = pygame.Surface((width * SCALE, height * SCALE), pygame.SRCALPHA)
    render_surface.fill((0, 0, 0))

    fade = pygame.Surface((width * SCALE, height * SCALE))

    r = 150
    g = 75
    b = 0
    ru = False
    gu = True
    bu = True

    star_layers = []
    for cfg in STAR_LAYERS:
        star_layers.append({
        "stars": init_stars(cfg["count"], width * SCALE, height * SCALE),
        "radius": cfg["radius"] * SCALE,
        "speed": cfg["speed"] * SCALE,
        "alpha": cfg["alpha"],
    })

    start_time = time.time()
    clock = pygame.time.Clock()
    while running:
        fade.set_alpha(stats.fade)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                preset_sober(stats)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                preset_200ug(stats)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                preset_500ug(stats)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                stats.chaos = not stats.chaos
            
        dt = clock.tick(100) / 1000.0
        dt = min(dt, 0.05) 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.try_start_move("UP", maze)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.try_start_move("DOWN", maze)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.try_start_move("LEFT", maze)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.try_start_move("RIGHT", maze)  # jamais plus de 50ms de mouvement simulé par frame
        player.update(dt)
        r = blblbl(r, ru)
        g = blblbl(g, gu)
        b = blblbl(b, bu)
        ru = ahahahah(r, ru)
        gu = ahahahah(g, gu)
        bu = ahahahah(b, bu)


        fade.fill((r, g, b))
        render_surface.blit(fade, (0, 0))
        for layer in star_layers:
            draw_stars(render_surface, layer["stars"], layer["speed"], width * SCALE, layer["radius"], layer["alpha"])

        elapsed = time.time() - start_time
        draw_maze(render_surface, maze, cell_size * SCALE, stats, elapsed, SCALE)
        draw_player(render_surface, player, cell_size * SCALE)

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
