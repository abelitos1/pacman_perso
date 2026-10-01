"""Background effects: wall wobble presets, colour cycling and stars."""
import random
from dataclasses import dataclass

import pygame


@dataclass
class VisualState:
    """Parameters of the wall animation (see ui.maze_view)."""

    bend: float = 0
    bend_speed: float = 0.05
    thick_l: float = 7
    thick_u: float = 7
    thick_speed: float = 0.2
    fade: float = 100
    chaos: bool = False


def preset_sober(stat: VisualState) -> None:
    """Key u: thin, still walls (default look)."""
    stat.bend = 0
    stat.bend_speed = 0.05
    stat.thick_l = 7
    stat.thick_u = 7
    stat.thick_speed = 0.2
    stat.fade = 100


def preset_200ug(stat: VisualState) -> None:
    """Key i: walls pulse in thickness, background trails."""
    stat.bend = 0
    stat.bend_speed = 0.05
    stat.thick_l = 2
    stat.thick_u = 15
    stat.thick_speed = 0.2
    stat.fade = 22


def preset_500ug(stat: VisualState) -> None:
    """Key o: walls pulse and bend, strong trails."""
    stat.bend = 1
    stat.bend_speed = 0.1
    stat.thick_l = 2
    stat.thick_u = 17
    stat.thick_speed = 0.25
    stat.fade = 15


class ColorCycle:
    """Background colour whose channels each bounce between 0 and 150,
    one step per frame."""

    MAX = 150

    def __init__(self) -> None:
        """Start from an orange-ish colour."""
        self.values = [150, 75, 0]
        self.rising = [False, True, True]

    def step(self) -> tuple[int, int, int]:
        """Advance one frame and return the new colour."""
        for i in range(3):
            self.values[i] += 1 if self.rising[i] else -1
            if self.values[i] == self.MAX:
                self.rising[i] = False
            elif self.values[i] == 0:
                self.rising[i] = True
        r, g, b = self.values
        return (r, g, b)


STAR_LAYERS = [
    {"count": 80, "radius": 0.5, "speed": -0.3, "alpha": 60},  # fond
    {"count": 50, "radius": 1, "speed": -0.8, "alpha": 110},   # milieu
    {"count": 25, "radius": 2, "speed": -1.6, "alpha": 170},   # avant
]


class StarLayer:
    """Stars scrolling horizontally at one speed (parallax layer)."""

    def __init__(self, count: int, radius: float, speed: float, alpha: int,
                 width: int, height: int) -> None:
        """Scatter `count` stars at random over a width x height area."""
        self.radius = radius
        self.speed = speed
        self.alpha = alpha
        self.width = width
        self.stars = [
            [random.uniform(0, width), random.uniform(0, height)]
            for _ in range(count)
        ]

    def draw(self, surface: pygame.Surface) -> None:
        """Scroll the stars one frame and draw them."""
        for star in self.stars:
            star[0] = (star[0] + self.speed) % self.width
            pygame.draw.circle(
                surface,
                (255, 255, 255, self.alpha),
                (int(star[0]), int(star[1])),
                self.radius,
            )


def make_star_layers(width: int, height: int) -> list[StarLayer]:
    """Build the parallax layers described by STAR_LAYERS."""
    return [
        StarLayer(
            count=int(cfg["count"]),
            radius=cfg["radius"],
            speed=cfg["speed"],
            alpha=int(cfg["alpha"]),
            width=width,
            height=height,
        )
        for cfg in STAR_LAYERS
    ]
