"""Main loop: events -> game update -> render."""
import pygame

from game.game_state import GameState
from ui.controls import read_direction
from ui.renderer import Renderer

FPS = 100
MAX_DT = 0.05  # never simulate more than 50 ms of movement per frame


def run(state: GameState, cell_size: int) -> None:
    pygame.init()
    renderer = Renderer(state, cell_size)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    renderer.handle_key(event.key)

        dt = min(clock.tick(FPS) / 1000.0, MAX_DT)
        state.update(dt, read_direction(pygame.key.get_pressed()))
        renderer.draw(state)

    pygame.quit()
