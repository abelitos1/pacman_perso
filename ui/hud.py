"""In-game HUD: score, lives, level, remaining time and cheat status."""
import pygame

from game.game_state import GameState

HUD_HEIGHT = 56
HUD_BG = (0, 0, 0)
HUD_TEXT = (255, 255, 255)
TIME_WARNING = (255, 80, 80)
TIME_WARNING_BELOW = 10  # seconds
CHEAT_COLOR = (255, 60, 200)
CHEAT_MARGIN = 10  # pixels from the top-left corner of the maze


class Hud:
    """Draws the status bar under the maze and the cheat badge."""

    def __init__(self) -> None:
        """Load the fonts (pygame's default one, no external file)."""
        self.font = pygame.font.Font(None, 44)
        self.small_font = pygame.font.Font(None, 30)

    def draw_bar(self, surface: pygame.Surface, state: GameState,
                 top: int) -> None:
        """Status bar: score, lives, level and remaining time.

        Args:
            surface: Where to draw.
            state: Current game.
            top: Y coordinate of the top of the bar.
        """
        width = surface.get_width()
        pygame.draw.rect(surface, HUD_BG, (0, top, width, HUD_HEIGHT))
        seconds = int(state.time_left + 0.999)
        items = [
            (f"Score: {state.score}", HUD_TEXT),
            (f"Lives: {state.player.lives}", HUD_TEXT),
            (f"Level: {state.level_index + 1}/{state.level_count}",
             HUD_TEXT),
            (f"Time: {seconds}",
             TIME_WARNING if seconds <= TIME_WARNING_BELOW else HUD_TEXT),
        ]
        slot = width / len(items)
        for i, (text, color) in enumerate(items):
            image = self.font.render(text, True, color)
            x = int(slot * i + (slot - image.get_width()) / 2)
            y = top + (HUD_HEIGHT - image.get_height()) // 2
            surface.blit(image, (x, y))

    def draw_cheats(self, surface: pygame.Surface, state: GameState) -> None:
        """While cheat mode is on, show it and the active toggle cheats
        in the top-left corner of the maze."""
        if not state.cheats.enabled:
            return
        text = " ".join(["CHEAT MODE"] + state.cheats.active_labels())
        image = self.small_font.render(text, True, CHEAT_COLOR, HUD_BG)
        surface.blit(image, (CHEAT_MARGIN, CHEAT_MARGIN))
