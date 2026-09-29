"""Menu screens: main menu, highscores, instructions, pause, game end."""
from typing import Optional

import pygame

from highscore.manager import (NAME_MAX_LENGTH, HighscoreEntry,
                               is_valid_name_char)

BASE_HEIGHT = 600  # layout values below are given for this height
MENU_SCREEN_SHARE = 0.8  # the menu window uses 80% of the screen height
MAX_MENU_HEIGHT = 1000
BACKGROUND = (0, 0, 0)
TITLE_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)
DIM_COLOR = (140, 140, 140)
SELECTED_COLOR = (255, 255, 0)
OVERLAY_ALPHA = 180
LINE_GAP = 0.25  # space under a line, as a share of its height

UP_KEYS = (pygame.K_UP, pygame.K_w)
DOWN_KEYS = (pygame.K_DOWN, pygame.K_s)
CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)

INSTRUCTIONS = [
    "Arrows / WASD: move   SPACE / ESC: pause",
    "U I O: visual presets   P: chaos walls",
    "",
    "Eat every pacgum to clear the level.",
    "Super-pacgums (corners) make ghosts edible.",
    "A ghost, or the timer running out, costs a life.",
    "Clear every level to win!",
    "",
    "TAB: cheat mode on/off, then:",
    "1 invincible   2 skip level   3 freeze ghosts",
    "4 extra life   5 speed x2   6 ghosts edible",
]


def menu_size(desktop: tuple[int, int]) -> tuple[int, int]:
    """Menu window size: 80% of the screen height, 4:3, fitting the screen.

    Args:
        desktop: Screen size in pixels.
    """
    height = min(int(desktop[1] * MENU_SCREEN_SHARE), MAX_MENU_HEIGHT)
    width = min(height * 4 // 3, int(desktop[0] * 0.9))
    return width, height


class Fonts:
    """The fonts used by the menus (pygame's default font), sized for
    the window height so the menus scale with the screen."""

    def __init__(self, window_height: int) -> None:
        """Load the default font at the sizes the menus use.

        Args:
            window_height: Height of the window the menus are drawn in.
        """
        self.scale = window_height / BASE_HEIGHT
        self.title = pygame.font.Font(None, self.px(96))
        self.big = pygame.font.Font(None, self.px(56))
        self.normal = pygame.font.Font(None, self.px(38))
        self.small = pygame.font.Font(None, self.px(28))

    def px(self, value: float) -> int:
        """Convert a length given for BASE_HEIGHT to the real window."""
        return int(value * self.scale)


def draw_centered(surface: pygame.Surface, font: pygame.font.Font,
                  text: str, color: tuple[int, int, int], y: int) -> int:
    """Draw `text` horizontally centered at height `y`.

    Returns:
        The y coordinate just below the text, plus a small gap.
    """
    image = font.render(text, True, color)
    surface.blit(image, ((surface.get_width() - image.get_width()) // 2, y))
    return y + int(image.get_height() * (1 + LINE_GAP))


class MenuList:
    """Vertical list of choices, navigated with Up/Down and Enter."""

    def __init__(self, items: list[str]) -> None:
        """Create the list with the first item selected."""
        self.items = items
        self.selected = 0

    def handle_key(self, key: int) -> Optional[str]:
        """Move the selection, or return the chosen item on confirm."""
        if key in UP_KEYS:
            self.selected = (self.selected - 1) % len(self.items)
        elif key in DOWN_KEYS:
            self.selected = (self.selected + 1) % len(self.items)
        elif key in CONFIRM_KEYS:
            return self.items[self.selected]
        return None

    def draw(self, surface: pygame.Surface, font: pygame.font.Font,
             y: int) -> int:
        """Draw the items from height `y`, the selected one highlighted.

        Returns:
            The y coordinate below the last item.
        """
        for i, item in enumerate(self.items):
            if i == self.selected:
                y = draw_centered(surface, font, f"> {item} <",
                                  SELECTED_COLOR, y)
            else:
                y = draw_centered(surface, font, item, TEXT_COLOR, y)
        return y


class NameInput:
    """Text field for the highscore name (letters, digits, spaces)."""

    def __init__(self) -> None:
        """Start with an empty name."""
        self.text = ""

    def handle_key(self, event: pygame.event.Event) -> None:
        """Apply one KEYDOWN event: type a character or erase one."""
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif (is_valid_name_char(event.unicode)
              and len(self.text) < NAME_MAX_LENGTH
              and not (event.unicode == " " and not self.text)):
            self.text += event.unicode


def draw_main_menu(surface: pygame.Surface, fonts: Fonts, menu: MenuList,
                   best: Optional[HighscoreEntry]) -> None:
    """Title, the main choices and the best score so far."""
    surface.fill(BACKGROUND)
    y = draw_centered(surface, fonts.title, "Pac-Man", TITLE_COLOR,
                      fonts.px(90))
    y = menu.draw(surface, fonts.normal, y + fonts.px(60))
    if best is not None:
        draw_centered(surface, fonts.small,
                      f"Best: {best.name} - {best.score} pts", DIM_COLOR,
                      y + fonts.px(40))
    draw_centered(surface, fonts.small, "Arrows + ENTER", DIM_COLOR,
                  surface.get_height() - fonts.px(50))


def draw_highscores(surface: pygame.Surface, fonts: Fonts,
                    entries: list[HighscoreEntry]) -> None:
    """The top 10 table."""
    surface.fill(BACKGROUND)
    y = draw_centered(surface, fonts.big, "Highscores", TITLE_COLOR,
                      fonts.px(50))
    y += fonts.px(10)
    if not entries:
        draw_centered(surface, fonts.normal, "No highscore yet",
                      DIM_COLOR, y)
    for rank, entry in enumerate(entries, start=1):
        y = draw_centered(surface, fonts.normal,
                          f"{rank}. {entry.name} - {entry.score} pts",
                          TEXT_COLOR, y)
    draw_centered(surface, fonts.small, "ESC or ENTER: back", DIM_COLOR,
                  surface.get_height() - fonts.px(50))


def draw_instructions(surface: pygame.Surface, fonts: Fonts) -> None:
    """Controls and rules."""
    surface.fill(BACKGROUND)
    y = draw_centered(surface, fonts.big, "Instructions", TITLE_COLOR,
                      fonts.px(50))
    y += fonts.px(10)
    for line in INSTRUCTIONS:
        y = draw_centered(surface, fonts.small, line, TEXT_COLOR, y)
    draw_centered(surface, fonts.small, "ESC or ENTER: back", DIM_COLOR,
                  surface.get_height() - fonts.px(50))


def draw_pause(surface: pygame.Surface, fonts: Fonts,
               menu: MenuList) -> None:
    """Darken the game view and show the pause choices on top."""
    shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, OVERLAY_ALPHA))
    surface.blit(shade, (0, 0))
    y = surface.get_height() // 2 - fonts.px(90)
    y = draw_centered(surface, fonts.big, "PAUSED", TITLE_COLOR, y)
    menu.draw(surface, fonts.normal, y + fonts.px(20))


def draw_game_end(surface: pygame.Surface, fonts: Fonts, won: bool,
                  score: int, name_input: Optional[NameInput]) -> None:
    """Final score, and the name prompt if the score made the top 10."""
    surface.fill(BACKGROUND)
    title = "YOU WIN!" if won else "GAME OVER"
    y = draw_centered(surface, fonts.title, title, TITLE_COLOR,
                      fonts.px(90))
    if won:
        y = draw_centered(surface, fonts.normal,
                          "Congratulations, every level cleared!",
                          TEXT_COLOR, y)
    y = draw_centered(surface, fonts.big, f"Score: {score}", TEXT_COLOR,
                      y + fonts.px(20))
    if name_input is None:
        draw_centered(surface, fonts.small, "ENTER: back to menu",
                      DIM_COLOR, y + fonts.px(60))
        return
    y = draw_centered(surface, fonts.normal,
                      "New highscore! Enter your name:", TEXT_COLOR,
                      y + fonts.px(40))
    cursor = "_" if len(name_input.text) < NAME_MAX_LENGTH else ""
    y = draw_centered(surface, fonts.big, name_input.text + cursor,
                      SELECTED_COLOR, y)
    draw_centered(surface, fonts.small,
                  "ENTER: save   ESC: skip", DIM_COLOR, y + fonts.px(30))
