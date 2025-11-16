"""Time formatting utilities."""

from datetime import datetime

from .types import DisplayOption


class TimeFormatter:
    """Formats time according to display options."""

    def __init__(self, options: list[DisplayOption]) -> None:
        """Initialize the formatter with display options."""
        self.options = options
        self._blink_state = True

    def get_current_time(self) -> datetime:
        """Get current time (UTC or local based on options)."""
        if DisplayOption.UTC in self.options:
            return datetime.utcnow()
        return datetime.now()

    def format_time(self, dt: datetime) -> str:
        """Format datetime as time string according to options."""
        # Determine hour format
        hour_fmt = "%I" if DisplayOption.TWELVE_HOUR in self.options else "%H"

        # Build time format string
        if DisplayOption.SHOW_SECONDS in self.options:
            time_fmt = f"{hour_fmt}:%M:%S"
        else:
            time_fmt = f"{hour_fmt}:%M"

        # Format the time
        time_str = dt.strftime(time_fmt)

        # Add AM/PM if enabled
        if DisplayOption.TWELVE_HOUR in self.options and DisplayOption.SHOW_AMPM in self.options:
            ampm = dt.strftime(" %p")
            time_str += ampm

        # Handle blinking colon
        if DisplayOption.BLINK_COLON in self.options:
            if not self._blink_state:
                time_str = time_str.replace(":", " ")
            self._blink_state = not self._blink_state

        # Remove leading zero in 12-hour format
        if DisplayOption.TWELVE_HOUR in self.options and time_str.startswith("0"):
            time_str = " " + time_str[1:]

        return time_str

    def format_date(self, dt: datetime) -> str:
        """Format datetime as detailed date string."""
        # Format: "Monday, January 01, 2025"
        return dt.strftime("%A, %B %d, %Y")

    def should_display_date(self) -> bool:
        """Check if date should be displayed."""
        return DisplayOption.SHOW_DATE in self.options
