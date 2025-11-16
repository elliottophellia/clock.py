"""Main clock application logic."""

from datetime import datetime

from .time_formatter import TimeFormatter
from .types import ClockConfig, DisplayOption


class Clock:
    """Manages clock state and update logic."""

    def __init__(self, config: ClockConfig) -> None:
        """Initialize the clock with configuration."""
        self.config = config
        self.formatter = TimeFormatter(config.options)
        self._last_update: datetime | None = None

    def should_update(self) -> bool:
        """Check if the display needs updating."""
        current_time = self.formatter.get_current_time()

        # Always update on first check
        if self._last_update is None:
            self._last_update = current_time
            return True

        # Always update if blinking colon is enabled
        if DisplayOption.BLINK_COLON in self.config.options:
            return True

        # Update when seconds change if showing seconds
        if DisplayOption.SHOW_SECONDS in self.config.options:
            should_update = current_time.second != self._last_update.second
        else:
            # Otherwise update when minutes change
            should_update = (
                current_time.minute != self._last_update.minute
                or current_time.hour != self._last_update.hour
            )

        self._last_update = current_time
        return should_update

    def get_display_strings(self) -> tuple[str, str | None]:
        """Get the formatted time and date strings for display."""
        dt = self.formatter.get_current_time()
        time_str = self.formatter.format_time(dt)
        date_str = self.formatter.format_date(dt) if self.formatter.should_display_date() else None
        return time_str, date_str
