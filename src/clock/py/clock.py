from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple


class ColorOption(Enum):
    """Color options for the clock."""

    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7


class ClockOption(Enum):
    """Clock display options."""

    TWELVE_HOUR = auto()
    SECONDS = auto()
    BOLD = auto()
    CENTER = auto()
    BLINK_COLON = auto()
    UTC = auto()
    DATE = auto()
    AMPM = auto()


@dataclass
class ClockConfig:
    """Configuration for the tty-clock."""

    color: ColorOption = ColorOption.GREEN
    delay: float = 1.0
    options: List[ClockOption] = None
    x: int = 0
    y: int = 0

    def __post_init__(self) -> None:
        """Initialize default options if none provided."""
        if self.options is None:
            self.options = []


class Clock:
    """Digital clock implementation."""

    # Digit representation in 5x6 grid
    DIGITS: Dict[str, List[str]] = {
        "0": [
            " ███ ",
            "█   █",
            "█   █",
            "█   █",
            "█   █",
            " ███ ",
        ],
        "1": [
            "  █  ",
            " ██  ",
            "  █  ",
            "  █  ",
            "  █  ",
            " ███ ",
        ],
        "2": [
            " ███ ",
            "█   █",
            "    █",
            " ███ ",
            "█    ",
            "█████",
        ],
        "3": [
            " ███ ",
            "█   █",
            "   ██",
            "   ██",
            "█   █",
            " ███ ",
        ],
        "4": [
            "   █ ",
            "  ██ ",
            " █ █ ",
            "█████",
            "   █ ",
            "   █ ",
        ],
        "5": [
            "█████",
            "█    ",
            "████ ",
            "    █",
            "█   █",
            " ███ ",
        ],
        "6": [
            " ███ ",
            "█    ",
            "████ ",
            "█   █",
            "█   █",
            " ███ ",
        ],
        "7": [
            "█████",
            "    █",
            "   █ ",
            "  █  ",
            " █   ",
            "█    ",
        ],
        "8": [
            " ███ ",
            "█   █",
            " ███ ",
            " ███ ",
            "█   █",
            " ███ ",
        ],
        "9": [
            " ███ ",
            "█   █",
            "█   █",
            " ████",
            "    █",
            " ███ ",
        ],
        ":": [
            "     ",
            "  █  ",
            "  █  ",
            "     ",
            "  █  ",
            "  █  ",
        ],
        " ": [
            "     ",
            "     ",
            "     ",
            "     ",
            "     ",
            "     ",
        ],
        "-": [
            "     ",
            "     ",
            "█████",
            "     ",
            "     ",
            "     ",
        ],
        "/": [
            "    █",
            "   █ ",
            "  █  ",
            " █   ",
            "█    ",
            "     ",
        ],
        "AM": [
            "  █████ █    █",
            "  █   █ ██  ██",
            "  █████ █ ██ █",
            "  █   █ █    █",
            "  █   █ █    █",
            "  █   █ █    █",
        ],
        "PM": [
            "  █████ █    █",
            "  █   █ ██  ██",
            "  █████ █ ██ █",
            "  █     █    █",
            "  █     █    █",
            "  █     █    █",
        ],
    }

    def __init__(self, config: ClockConfig) -> None:
        """Initialize the clock with given configuration."""
        self.config = config
        self._blink_state = True
        self._last_time: Optional[datetime] = None

    def get_time(self) -> datetime:
        """Get the current time based on configuration."""
        if ClockOption.UTC in self.config.options:
            return datetime.utcnow()
        return datetime.now()

    def format_time(self, dt: datetime) -> str:
        """Format time according to configuration options."""
        hour_fmt = "%I" if ClockOption.TWELVE_HOUR in self.config.options else "%H"

        if ClockOption.SECONDS in self.config.options:
            time_fmt = f"{hour_fmt}:%M:%S"
        else:
            time_fmt = f"{hour_fmt}:%M"

        # Format the basic time string
        time_str = dt.strftime(time_fmt)

        # Add AM/PM if both 12-hour and AMPM options are enabled
        if (ClockOption.TWELVE_HOUR in self.config.options and
            ClockOption.AMPM in self.config.options):
            ampm = dt.strftime(" %p")
            time_str += ampm

        # Handle blinking colon
        if ClockOption.BLINK_COLON in self.config.options:
            if not self._blink_state:
                time_str = time_str.replace(":", " ")
            self._blink_state = not self._blink_state

        # Remove leading zero in 12-hour format
        if ClockOption.TWELVE_HOUR in self.config.options and time_str.startswith("0"):
            time_str = " " + time_str[1:]

        return time_str

    def format_date(self, dt: datetime) -> str:
        """Format date for display."""
        return dt.strftime("%Y-%m-%d")

    def get_display_info(self) -> Tuple[str, Optional[str]]:
        """Get the time and date strings to display."""
        dt = self.get_time()
        time_str = self.format_time(dt)
        date_str = self.format_date(dt) if ClockOption.DATE in self.config.options else None
        return time_str, date_str

    def should_update(self) -> bool:
        """Check if the display needs updating."""
        current_time = self.get_time()

        # Always update if this is the first check
        if self._last_time is None:
            self._last_time = current_time
            return True

        # If blinking colon is enabled, we need to update every tick
        if ClockOption.BLINK_COLON in self.config.options:
            return True

        # If seconds are displayed, update when seconds change
        if ClockOption.SECONDS in self.config.options:
            should_update = current_time.second != self._last_time.second
        else:
            # Otherwise update when minutes change
            should_update = (current_time.minute != self._last_time.minute or
                            current_time.hour != self._last_time.hour)

        self._last_time = current_time
        return should_update

    def get_dimensions(self, time_str: str, date_str: Optional[str]) -> Tuple[int, int]:
        """Calculate the dimensions needed to display the clock."""
        # Split time string into main time and AM/PM if present
        main_time = time_str
        has_ampm = False

        if (ClockOption.TWELVE_HOUR in self.config.options and
            ClockOption.AMPM in self.config.options):
            parts = time_str.split()
            main_time = parts[0]
            has_ampm = len(parts) > 1

        # Each digit is 5 characters wide plus 1 space between digits
        width = len(main_time) * 6 - 1  # -1 because no space needed after last digit

        # Add width for AM/PM if present
        if has_ampm:
            width += len(self.DIGITS["AM"][0]) + 1  # Width of AM/PM digit pattern plus space

        # Height is 6 for the time digits
        height = 6

        # Add space for date if needed
        if date_str:
            width = max(width, len(date_str))
            height += 2  # Add 1 line for date and 1 for spacing

        return width, height
