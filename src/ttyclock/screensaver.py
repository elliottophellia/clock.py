"""Screensaver mode with bouncing clock animation."""

import random
from typing import TYPE_CHECKING

from .types import Color, DisplayOption

if TYPE_CHECKING:
    from .types import ClockConfig


class Screensaver:
    """Manages screensaver bouncing animation and random colors."""

    def __init__(self, config: "ClockConfig") -> None:
        """Initialize screensaver with configuration."""
        self.config = config
        self.x = 0
        self.y = 0
        self.velocity_x = 1
        self.velocity_y = 1
        self.current_color = config.color
        self._color_change_counter = 0
        self._color_change_interval = 30  # Change color every 30 updates

    def update_position(self, width: int, height: int, max_x: int, max_y: int) -> tuple[int, int]:
        """Update bouncing position and return new coordinates."""
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Bounce off edges
        if self.x <= 0 or self.x + width >= max_x:
            self.velocity_x *= -1
            self.x = max(0, min(self.x, max_x - width))
            # Change color on horizontal bounce if random colors enabled
            if DisplayOption.RANDOM_COLOR in self.config.options:
                self._change_color()

        if self.y <= 0 or self.y + height >= max_y:
            self.velocity_y *= -1
            self.y = max(0, min(self.y, max_y - height))
            # Change color on vertical bounce if random colors enabled
            if DisplayOption.RANDOM_COLOR in self.config.options:
                self._change_color()

        return self.x, self.y

    def _change_color(self) -> None:
        """Change to a random color."""
        colors = [c for c in Color if c != self.current_color]
        if colors:
            self.current_color = random.choice(colors)

    def get_color(self) -> Color:
        """Get current color (may be random)."""
        if DisplayOption.RANDOM_COLOR in self.config.options:
            # Periodically change color even without bouncing
            self._color_change_counter += 1
            if self._color_change_counter >= self._color_change_interval:
                self._change_color()
                self._color_change_counter = 0
            return self.current_color
        return self.config.color

    def reset_position(self, max_x: int, max_y: int) -> None:
        """Reset to random position when terminal resizes."""
        self.x = random.randint(0, max(0, max_x - 50))
        self.y = random.randint(0, max(0, max_y - 10))
        # Random initial direction
        self.velocity_x = random.choice([-1, 1])
        self.velocity_y = random.choice([-1, 1])
