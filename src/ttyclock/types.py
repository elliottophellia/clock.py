"""Type definitions and enums for the clock application."""

from dataclasses import dataclass, field
from enum import Enum, auto


class Color(Enum):
    """Available terminal colors."""

    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7


class DisplayOption(Enum):
    """Display configuration options."""

    TWELVE_HOUR = auto()
    SHOW_SECONDS = auto()
    BOLD = auto()
    CENTER = auto()
    BLINK_COLON = auto()
    UTC = auto()
    SHOW_DATE = auto()
    SHOW_AMPM = auto()
    SCREENSAVER = auto()
    RANDOM_COLOR = auto()


@dataclass
class Position:
    """Screen position coordinates."""

    x: int = 0
    y: int = 0


@dataclass
class ClockConfig:
    """Configuration for the clock display."""

    color: Color = Color.GREEN
    delay: float = 0.1
    options: list[DisplayOption] = field(default_factory=list)
    position: Position = field(default_factory=Position)
    font: str = "block"  # Font name: block, slim, dot, bold, mini
