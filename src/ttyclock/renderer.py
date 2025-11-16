"""Terminal rendering for the clock display."""

import contextlib
import curses
from typing import Any

from .digits import DIGIT_HEIGHT, DIGIT_SPACING, calculate_width, get_pattern
from .types import ClockConfig, DisplayOption


class ClockRenderer:
    """Handles rendering the clock to the terminal."""

    def __init__(self, config: ClockConfig) -> None:
        """Initialize the renderer with configuration."""
        self.config = config

    def _get_display_dimensions(self, time_str: str, date_str: str | None) -> tuple[int, int]:
        """Calculate dimensions needed for display."""
        # Split time string for AM/PM handling
        main_time = time_str
        has_ampm = False

        if DisplayOption.TWELVE_HOUR in self.config.options and DisplayOption.SHOW_AMPM in self.config.options:
            parts = time_str.split()
            main_time = parts[0]
            has_ampm = len(parts) > 1

        # Calculate time width using selected font
        time_width = calculate_width(main_time, self.config.font)

        # Add AM/PM width if present
        if has_ampm:
            ampm_pattern = get_pattern("AM", self.config.font)
            time_width += len(ampm_pattern[0]) + DIGIT_SPACING

        # Height starts with time digits
        height = DIGIT_HEIGHT
        width = time_width

        # Add date dimensions if needed
        if date_str:
            # Add spacing before date
            height += 2
            # Date gets its own line, use max of time or date width
            width = max(width, len(date_str))
            height += 1  # Date line itself

        return width, height

    def _get_position(
        self, width: int, height: int, max_x: int, max_y: int, override_pos: tuple[int, int] | None = None
    ) -> tuple[int, int]:
        """Calculate position on screen."""
        # Screensaver mode uses override position
        if override_pos is not None:
            return override_pos

        if DisplayOption.CENTER in self.config.options:
            x = max(0, (max_x - width) // 2)
            y = max(0, (max_y - height) // 2)
        else:
            x = min(self.config.position.x, max(0, max_x - width))
            y = min(self.config.position.y, max(0, max_y - height))

        return x, y

    def _draw_digit(
        self, win: Any, y: int, x: int, char: str, color_pair: int, use_bold: bool
    ) -> int:
        """Draw a single character and return its width."""
        pattern = get_pattern(char, self.config.font)
        attr = curses.A_BOLD if use_bold else 0

        width = len(pattern[0])

        for row_idx, row in enumerate(pattern):
            for col_idx, pixel in enumerate(row):
                # Render any non-space character
                if pixel != " ":
                    # Ignore errors at screen boundaries
                    with contextlib.suppress(curses.error):
                        # Use the actual character from the pattern
                        win.addch(
                            y + row_idx,
                            x + col_idx,
                            pixel,
                            attr | curses.color_pair(color_pair),
                        )

        return width

    def _draw_centered_text(
        self, win: Any, y: int, text: str, width: int, x_offset: int, color_pair: int
    ) -> None:
        """Draw centered text within a given width."""
        text_x = x_offset + max(0, (width - len(text)) // 2)
        with contextlib.suppress(curses.error):
            win.addstr(y, text_x, text, curses.color_pair(color_pair))

    def _draw_error_message(self, win: Any, max_y: int, max_x: int, message: str) -> None:
        """Draw error message centered on screen."""
        # Calculate center position
        y = max(0, max_y // 2)
        x = max(0, (max_x - len(message)) // 2)

        # Draw with some style
        color_pair = 2  # Red color
        attr = curses.A_BOLD

        with contextlib.suppress(curses.error):
            # Draw a simple border
            if max_x > len(message) + 4 and max_y > 2:
                border_len = len(message) + 2
                border_x = max(0, (max_x - border_len) // 2)

                # Top border
                win.addstr(y - 1, border_x, "┌" + "─" * (border_len - 2) + "┐", attr)
                # Message
                win.addstr(y, border_x, "│ ", attr)
                win.addstr(y, x, message, curses.color_pair(color_pair) | attr)
                win.addstr(y, border_x + border_len - 1, "│", attr)
                # Bottom border
                win.addstr(y + 1, border_x, "└" + "─" * (border_len - 2) + "┘", attr)
            else:
                # Just draw the message if no space for border
                win.addstr(y, x, message, curses.color_pair(color_pair) | attr)

    def render(
        self,
        win: Any,
        max_y: int,
        max_x: int,
        time_str: str,
        date_str: str | None,
        override_pos: tuple[int, int] | None = None,
        override_color: int | None = None,
    ) -> None:
        """Render the clock to the window."""
        # Parse time string for AM/PM
        main_time = time_str
        is_pm = False
        show_ampm = False

        if DisplayOption.TWELVE_HOUR in self.config.options and DisplayOption.SHOW_AMPM in self.config.options:
            parts = time_str.split()
            main_time = parts[0]
            if len(parts) > 1:
                is_pm = parts[1] == "PM"
                show_ampm = True

        # Calculate dimensions and position
        width, height = self._get_display_dimensions(time_str, date_str)
        x, y = self._get_position(width, height, max_x, max_y, override_pos)

        # Check if display fits
        if x + width > max_x or y + height > max_y:
            self._draw_error_message(win, max_y, max_x, "Terminal too small")
            return

        # Get display attributes
        color_pair = override_color if override_color is not None else self.config.color.value + 1
        use_bold = DisplayOption.BOLD in self.config.options

        # Clear display area with some padding
        clear_width = width + 2
        clear_height = height + 2
        for row in range(clear_height):
            with contextlib.suppress(curses.error):
                win.addstr(max(0, y - 1) + row, max(0, x - 1), " " * clear_width)

        # Calculate time width for centering
        time_width = calculate_width(main_time, self.config.font)
        if show_ampm:
            ampm_pattern = get_pattern("AM", self.config.font)
            time_width += len(ampm_pattern[0]) + DIGIT_SPACING

        # Center time within available width
        time_x = x + max(0, (width - time_width) // 2)

        # Draw time digits
        current_x = time_x
        for char in main_time:
            char_width = self._draw_digit(win, y, current_x, char, color_pair, use_bold)
            current_x += char_width + DIGIT_SPACING

        # Draw AM/PM if needed
        if show_ampm:
            ampm_char = "PM" if is_pm else "AM"
            self._draw_digit(win, y, current_x, ampm_char, color_pair, use_bold)

        # Draw date if needed
        if date_str:
            # Position date below time with spacing
            date_y = y + DIGIT_HEIGHT + 2

            # Draw decorative separator
            separator_y = y + DIGIT_HEIGHT + 1
            separator = "─" * min(width, len(date_str))
            separator_x = x + max(0, (width - len(separator)) // 2)
            with contextlib.suppress(curses.error):
                win.addstr(
                    separator_y,
                    separator_x,
                    separator,
                    curses.color_pair(color_pair) | curses.A_DIM,
                )

            # Draw centered date
            self._draw_centered_text(win, date_y, date_str, width, x, color_pair)
