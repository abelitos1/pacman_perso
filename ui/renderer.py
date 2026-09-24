import sys
import pygame
import time
from game.maze_loader import Maze
from config.loader import load_config
from game.game_state import build_level_maze
import random

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
LINE_W = 5
BEND = 0
THICKL = 3
THICKU = 15

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


def draw_maze(screen, maze, cell_size, n, e, un, ue):
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.cells[y][x]
            px, py = x * cell_size, y * cell_size

            if cell.wall_north:
                pygame.draw.line(screen, WHITE, (px, py - un), (px + cell_size, py + un),int(n))
                # pygame.draw.circle(screen, WHITE, (px, py),int(n)//2)
                # pygame.draw.circle(screen, WHITE, (px + cell_size, py),int(n)//2)
            if cell.wall_west:
                pygame.draw.line(screen, WHITE, (px + ue, py), (px - ue, py + cell_size), int(e))
                # pygame.draw.circle(screen, WHITE, (px, py),int(e)//2)
                # pygame.draw.circle(screen, WHITE, (px, py + cell_size),int(e)//2)
            if cell.wall_south:
                pygame.draw.line(screen, WHITE, (px, py + cell_size - un), (px + cell_size, py + cell_size + un), int(n))
                # pygame.draw.circle(screen, WHITE, (px, py + cell_size),int(n)//2)
                # pygame.draw.circle(screen, WHITE, (px + cell_size, py + cell_size),int(n)//2)
            if cell.wall_east:
                pygame.draw.line(screen, WHITE, (px + cell_size + ue, py), (px + cell_size - ue, py + cell_size), int(e))
                # pygame.draw.circle(screen, WHITE, (px + cell_size, py),int(e)//2)
                # pygame.draw.circle(screen, WHITE, (px + cell_size, py + cell_size),int(e)//2)


def run_window(maze: Maze, cell_size : int) -> None:
    pygame.init()
    width = maze.width * cell_size
    height = maze.height * cell_size
    screen = pygame.display.set_mode((width, height))
    running = True

    r = 150
    g = 75
    b = 0
    ru = False
    gu = True
    bu = True
    widths = [3, 10]
    bend = [-3, 3]
    ubend = [1, -1]
    uwidths = [1, -1]
    fade = pygame.Surface((width, height))
    fade.fill((0, 0, 0))
    fade.set_alpha(25)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            
        screen.fill((r, g, b))
        r = blblbl(r, ru)
        g = blblbl(g, gu)
        b = blblbl(b, bu)
        ru = ahahahah(r, ru)
        gu = ahahahah(g, gu)
        bu = ahahahah(b, bu)
        for i in range(2):
            widths[i] += uwidths[i] * 0.1
            if widths[i] >= THICKU:
                widths[i] = THICKU
                uwidths[i] = -1
            elif widths[i] <= THICKL:
                widths[i] = THICKL
                uwidths[i] = 1

        for i in range(2):
            bend[i] += ubend[i] * 0.05
            if bend[i] >= BEND:
                bend[i] = BEND
                ubend[i] = -1
            elif bend[i] <= -BEND:
                bend[i] = -BEND
                ubend[i] = 1


        time.sleep(0.010)
        print(bend[0], bend[1])
        draw_maze(screen, maze, cell_size, widths[0], widths[1], bend[0], bend[1])
        pygame.draw.rect(screen, WHITE, (0,0, maze.width * cell_size, maze.height * cell_size), 7)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    config = load_config("config.json")
    maze = build_level_maze(config, level_index=0)
    run_window(maze, 40)