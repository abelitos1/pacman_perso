"""Main loop and screen flow.

Main menu > start game > win or lose > enter name for highscore > back
to the main menu (the flow asked by the subject).
"""
from enum import Enum
from typing import Optional

import pygame

from config.loader import Config
from game.game_state import GameState, Status
from highscore.manager import HighscoreManager
from ui.controls import CHEAT_MODE_KEY, cheat_for_key, direction_for_key
from ui.menu import (Fonts, MenuList, NameInput, draw_game_end,
                     draw_highscores, draw_instructions, draw_main_menu,
                     draw_pause, menu_size)
from ui.renderer import Renderer, desktop_size

FPS = 100
MAX_DT = 0.05  # never simulate more than 50 ms of movement per frame
BACK_KEYS = (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER,
             pygame.K_SPACE)

START, HIGHSCORES, INSTRUCTIONS, EXIT = (
    "Start Game", "Highscores", "Instructions", "Exit")
RESUME, MAIN_MENU = "Resume", "Main Menu"


class Screen(Enum):
    """Which screen is currently shown."""

    MAIN_MENU = "main_menu"
    HIGHSCORES = "highscores"
    INSTRUCTIONS = "instructions"
    PLAYING = "playing"
    GAME_END = "game_end"


class App:
    """Owns the window and switches between menus and the game."""

    def __init__(self, config: Config, highscores: HighscoreManager,
                 cell_size: int) -> None:
        """Initialise pygame and show the main menu.

        Args:
            config: Game settings, used for each new game.
            highscores: Already loaded highscore table.
            cell_size: Preferred cell size in pixels during the game.
        """
        pygame.init()
        self.config = config
        self.highscores = highscores
        self.cell_size = cell_size
        self.desktop = desktop_size()
        self.menu_size = menu_size(self.desktop)
        self.fonts = Fonts(self.menu_size[1])
        self.main_menu = MenuList([START, HIGHSCORES, INSTRUCTIONS, EXIT])
        self.pause_menu = MenuList([RESUME, MAIN_MENU])
        self.state: Optional[GameState] = None
        self.renderer: Optional[Renderer] = None
        self.name_input: Optional[NameInput] = None
        self.running = True
        self.window = self._open_menu_window()
        self.screen = Screen.MAIN_MENU

    def _open_menu_window(self) -> pygame.Surface:
        """Resize the window for the menus."""
        pygame.display.set_caption("Pac-Man")
        return pygame.display.set_mode(self.menu_size)

    def _go_to_menu(self) -> None:
        """Drop the current game and show the main menu."""
        self.state = self.renderer = self.name_input = None
        self.window = self._open_menu_window()
        self.screen = Screen.MAIN_MENU

    def _start_game(self) -> None:
        """Generate level 1 and switch to the game view."""
        self.state = GameState.new_game(self.config)
        self.renderer = Renderer(self.state, self.cell_size, self.desktop)
        self.pause_menu.selected = 0
        self.screen = Screen.PLAYING

    def _end_game(self, state: GameState) -> None:
        """Show the final score, with a name prompt if it is a highscore."""
        self.renderer = None
        self.name_input = (NameInput()
                           if self.highscores.qualifies(state.score)
                           else None)
        self.window = self._open_menu_window()
        self.screen = Screen.GAME_END

    def _on_main_menu_key(self, key: int) -> None:
        """Navigate the main menu."""
        choice = self.main_menu.handle_key(key)
        if choice == START:
            self._start_game()
        elif choice == HIGHSCORES:
            self.screen = Screen.HIGHSCORES
        elif choice == INSTRUCTIONS:
            self.screen = Screen.INSTRUCTIONS
        elif choice == EXIT or key == pygame.K_ESCAPE:
            self.running = False

    def _on_game_key(self, event: pygame.event.Event,
                     state: GameState) -> Optional[str]:
        """Handle a key during the game.

        Returns:
            The direction asked by the player, if the key was a move.
        """
        key = event.key
        if state.paused:
            if key == pygame.K_ESCAPE:
                state.toggle_pause()
                return None
            choice = self.pause_menu.handle_key(key)
            if choice == RESUME:
                state.toggle_pause()
            elif choice == MAIN_MENU:
                self._go_to_menu()
            return None
        if key in (pygame.K_ESCAPE, pygame.K_SPACE):
            self.pause_menu.selected = 0
            state.toggle_pause()
            return None
        if key == CHEAT_MODE_KEY:
            state.toggle_cheat_mode()
            return None
        cheat = cheat_for_key(key)
        if cheat is not None:
            state.use_cheat(cheat)
            return None
        if self.renderer is not None:
            self.renderer.handle_key(key)
        return direction_for_key(key)

    def _on_game_end_key(self, event: pygame.event.Event,
                         state: Optional[GameState]) -> None:
        """Type the name, save it on Enter, skip with Escape."""
        key = event.key
        if self.name_input is None:
            if key in BACK_KEYS:
                self._go_to_menu()
            return
        if key == pygame.K_ESCAPE:
            self._go_to_menu()
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.name_input.text.strip() and state is not None:
                self.highscores.add(self.name_input.text, state.score)
                self.highscores.save()
                self._go_to_menu()
        else:
            self.name_input.handle_key(event)

    def _handle_events(self) -> Optional[str]:
        """Process the pending events.

        Returns:
            The last direction asked this frame while playing, if any.
        """
        direction: Optional[str] = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type != pygame.KEYDOWN:
                continue
            elif self.screen is Screen.MAIN_MENU:
                self._on_main_menu_key(event.key)
            elif self.screen in (Screen.HIGHSCORES, Screen.INSTRUCTIONS):
                if event.key in BACK_KEYS:
                    self.screen = Screen.MAIN_MENU
            elif self.screen is Screen.PLAYING and self.state is not None:
                direction = self._on_game_key(event, self.state) or direction
            elif self.screen is Screen.GAME_END:
                self._on_game_end_key(event, self.state)
        return direction

    def _draw(self) -> None:
        """Draw the current screen and show it."""
        if self.screen is Screen.MAIN_MENU:
            best = (self.highscores.entries[0]
                    if self.highscores.entries else None)
            draw_main_menu(self.window, self.fonts, self.main_menu, best)
        elif self.screen is Screen.HIGHSCORES:
            draw_highscores(self.window, self.fonts, self.highscores.entries)
        elif self.screen is Screen.INSTRUCTIONS:
            draw_instructions(self.window, self.fonts)
        elif self.screen is Screen.GAME_END and self.state is not None:
            draw_game_end(self.window, self.fonts,
                          self.state.status is Status.VICTORY,
                          self.state.score, self.name_input)
        elif (self.screen is Screen.PLAYING and self.state is not None
              and self.renderer is not None):
            self.renderer.draw(self.state)
            if self.state.paused:
                draw_pause(self.renderer.screen, self.fonts, self.pause_menu)
        pygame.display.flip()

    def run(self) -> None:
        """Run until the player exits, then close the window."""
        clock = pygame.time.Clock()
        while self.running:
            dt = min(clock.tick(FPS) / 1000.0, MAX_DT)
            direction = self._handle_events()
            state = self.state
            if self.screen is Screen.PLAYING and state is not None:
                state.update(dt, direction)
                if state.is_over:
                    self._end_game(state)
            self._draw()
        pygame.quit()
