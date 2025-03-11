import argparse
import curses
import sys
import time
from typing import Any, Dict, Optional, Union

from .clock import Clock, ClockConfig, ClockOption, ColorOption
from .config import load_config, save_config, config_to_options


def parse_args() -> Dict[str, Any]:
    """Parse command line arguments and return configuration."""
    parser = argparse.ArgumentParser(description="Basically tty-clock but rewritten in Python")
    parser.add_argument(
        "-c", "--center", action="store_true", help="Center the clock in the terminal"
    )
    parser.add_argument(
        "-s", "--seconds", action="store_true", help="Show seconds in the clock"
    )
    parser.add_argument(
        "-b", "--bold", action="store_true", help="Use bold characters"
    )
    parser.add_argument(
        "-t", "--twelve", action="store_true", help="Use 12-hour format"
    )
    parser.add_argument(
        "-P", "--ampm", action="store_true",
        help="Show AM/PM indicator in 12-hour format"
    )
    parser.add_argument(
        "-k", "--blink", action="store_true", help="Blink the colon"
    )
    parser.add_argument(
        "-u", "--utc", action="store_true", help="Use UTC time"
    )
    parser.add_argument(
        "-d", "--date", action="store_true", help="Show current date"
    )
    parser.add_argument(
        "-C", "--color", type=int, choices=range(8), default=None,
        help="Set the clock color (0-7)"
    )
    parser.add_argument(
        "-x", type=int, default=None, help="Set the clock's x position"
    )
    parser.add_argument(
        "-y", type=int, default=None, help="Set the clock's y position"
    )
    parser.add_argument(
        "-D", "--delay", type=float, default=None,
        help="Set the update delay (seconds)"
    )
    parser.add_argument(
        "-S", "--save-config", action="store_true",
        help="Save current settings to config file"
    )

    return vars(parser.parse_args())


def args_to_config(args: Dict[str, Any], base_config: Dict[str, Any]) -> Dict[str, Any]:
    """Convert parsed arguments to configuration format."""
    config = base_config.copy()

    # Update options if specified
    if args["center"]:
        config["options"]["center"] = True
    if args["seconds"]:
        config["options"]["show_seconds"] = True
    if args["bold"]:
        config["options"]["bold"] = True
    if args["twelve"]:
        config["options"]["twelve_hour"] = True
    if args["blink"]:
        config["options"]["blink_colon"] = True
    if args["utc"]:
        config["options"]["utc"] = True
    if args["date"]:
        config["options"]["show_date"] = True
    if args["ampm"]:
        config["options"]["show_ampm"] = True

    # Update other settings if specified
    if args["color"] is not None:
        color_names = [color.name for color in ColorOption]
        config["color"] = color_names[args["color"]]

    if args["delay"] is not None:
        config["delay"] = args["delay"]

    if args["x"] is not None:
        config["position"]["x"] = args["x"]

    if args["y"] is not None:
        config["position"]["y"] = args["y"]

    return config


def setup_curses(stdscr) -> None:
    """Setup the curses environment."""
    curses.curs_set(0)  # Hide cursor
    curses.start_color()
    curses.use_default_colors()

    # Initialize color pairs for each color option
    for color in ColorOption:
        curses.init_pair(color.value + 1, color.value, -1)  # -1 for default background

    stdscr.clear()
    stdscr.nodelay(True)  # Non-blocking input


def draw_digit(win: Union['curses._CursesWindow', 'curses.window'],
              y: int, x: int, digit: str, bold: bool, color_pair: int) -> int:
    """Draw a single digit on the screen and return its width."""
    digit_pattern = Clock.DIGITS.get(digit, Clock.DIGITS[" "])
    attr = curses.A_BOLD if bold else 0

    width = len(digit_pattern[0])  # Width of the digit pattern

    for row, line in enumerate(digit_pattern):
        for col, char in enumerate(line):
            if char == "█":  # Only draw the filled parts
                win.addch(y + row, x + col, " ", attr | curses.color_pair(color_pair) | curses.A_REVERSE)

    return width


def draw_am_pm(win: Union['curses._CursesWindow', 'curses.window'],
              y: int, x: int, is_pm: bool, bold: bool, color_pair: int) -> None:
    """Draw the AM/PM indicator."""
    am_pm = "PM" if is_pm else "AM"
    digit_pattern = Clock.DIGITS.get(am_pm, Clock.DIGITS[" "])
    attr = curses.A_BOLD if bold else 0

    for row, line in enumerate(digit_pattern):
        for col, char in enumerate(line):
            if char == "█":  # Only draw the filled parts
                win.addch(y + row, x + col, " ", attr | curses.color_pair(color_pair) | curses.A_REVERSE)


def draw_clock(
    win: Union['curses._CursesWindow', 'curses.window'],
    clock: Clock, max_y: int, max_x: int,
    time_str: str, date_str: Optional[str]
) -> None:
    """Draw the clock on the screen."""
    # Split time string into main time and AM/PM indicator if present
    main_time = time_str
    is_pm = False
    show_ampm = False

    if (ClockOption.TWELVE_HOUR in clock.config.options and
        ClockOption.AMPM in clock.config.options):
        parts = time_str.split()
        main_time = parts[0]
        if len(parts) > 1:
            is_pm = parts[1] == "PM"
            show_ampm = True

    width, height = clock.get_dimensions(time_str, date_str)

    # Calculate position
    x, y = clock.config.x, clock.config.y
    if ClockOption.CENTER in clock.config.options:
        x = max(0, (max_x - width) // 2)
        y = max(0, (max_y - height) // 2)

    # Make sure the clock fits on screen
    if x + width > max_x or y + height > max_y:
        # Try to adjust position to fit if possible
        if ClockOption.CENTER not in clock.config.options:
            x = max(0, max_x - width)
            y = max(0, max_y - height)
            if x + width > max_x or y + height > max_y:
                # If still doesn't fit, show an error message if possible
                if max_y > 0 and max_x > 15:
                    win.addstr(0, 0, "Terminal too small")
                return
        else:
            # If still doesn't fit, show an error message if possible
            if max_y > 0 and max_x > 15:
                win.addstr(0, 0, "Terminal too small")
            return

    color_pair = clock.config.color.value + 1
    use_bold = ClockOption.BOLD in clock.config.options

    # Clear the area first (only the exact area needed)
    for row in range(height):
        win.addstr(y + row, x, " " * width)

    # Draw main time digits
    digit_x = x
    for char in main_time:
        char_width = draw_digit(win, y, digit_x, char, use_bold, color_pair)
        digit_x += char_width + 1  # Add 1 space between digits

    # Draw AM/PM if present
    if show_ampm:
        draw_am_pm(win, y, digit_x, is_pm, use_bold, color_pair)

    # Draw date if needed
    if date_str:
        date_y = y + 7  # Below the time with 1 line space
        win.addstr(date_y, x, date_str, curses.color_pair(color_pair))


def main() -> None:
    """Run the clock application."""
    # Parse command line arguments
    args = parse_args()

    # Load configuration
    config = load_config()

    # Apply command-line overrides
    config = args_to_config(args, config)

    # Save configuration if requested
    if args["save_config"]:
        save_config(config)
        print("Configuration saved to ~/.config/clock-py/config.json")
        if not any(args[opt] for opt in ["center", "seconds", "bold", "twelve", "blink", "utc", "date", "color", "x", "y", "delay"]):
            return  # Exit after saving if no display options given

    # Convert config to ClockConfig
    clock_options = config_to_options(config)
    clock_config = ClockConfig(
        color=clock_options["color"],
        delay=clock_options["delay"],
        options=clock_options["options"],
        x=clock_options["x"],
        y=clock_options["y"]
    )
    clock = Clock(clock_config)

    def curses_main(stdscr) -> None:
        setup_curses(stdscr)
        last_drawn_time = None
        last_drawn_date = None

        while True:
            # Check for quit key (q or ESC)
            try:
                key = stdscr.getch()
                if key in (ord('q'), ord('Q'), 27):  # 27 is ESC
                    break
            except:
                pass

            # Update clock if needed
            if clock.should_update():
                time_str, date_str = clock.get_display_info()

                # Only redraw if the display info has changed
                if time_str != last_drawn_time or date_str != last_drawn_date:
                    max_y, max_x = stdscr.getmaxyx()
                    draw_clock(stdscr, clock, max_y, max_x, time_str, date_str)
                    stdscr.refresh()
                    last_drawn_time = time_str
                    last_drawn_date = date_str

            time.sleep(clock_config.delay)

    try:
        curses.wrapper(curses_main)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
