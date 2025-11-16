"""Main entry point for the ttyclock application."""

import argparse
import curses
import sys
import time
from typing import Any

from .clock import Clock
from .config import (
    dict_to_clock_config,
    load_config,
    save_config,
)
from .renderer import ClockRenderer
from .screensaver import Screensaver
from .types import Color, DisplayOption


def parse_arguments() -> dict[str, Any]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Basically tty-clock but rewritten in Python"
    )
    parser.add_argument(
        "-c", "--center", action="store_true", help="Center the clock in the terminal"
    )
    parser.add_argument(
        "-s", "--seconds", action="store_true", help="Show seconds in the clock"
    )
    parser.add_argument("-b", "--bold", action="store_true", help="Use bold characters")
    parser.add_argument("-t", "--twelve", action="store_true", help="Use 12-hour format")
    parser.add_argument(
        "-P",
        "--ampm",
        action="store_true",
        help="Show AM/PM indicator in 12-hour format",
    )
    parser.add_argument("-k", "--blink", action="store_true", help="Blink the colon")
    parser.add_argument("-u", "--utc", action="store_true", help="Use UTC time")
    parser.add_argument("-d", "--date", action="store_true", help="Show current date")
    parser.add_argument(
        "-r", "--screensaver", action="store_true", help="Screensaver mode (bouncing clock)"
    )
    parser.add_argument(
        "-R",
        "--random-color",
        action="store_true",
        help="Random color changes in screensaver mode",
    )
    parser.add_argument(
        "-C",
        "--color",
        type=int,
        choices=range(8),
        default=None,
        help="Set the clock color (0-7)",
    )
    parser.add_argument(
        "-f",
        "--font",
        type=str,
        choices=["block", "slim", "dot", "bold", "mini"],
        default=None,
        help="Set the clock font (block, slim, dot, bold, mini)",
    )
    parser.add_argument("-x", type=int, default=None, help="Set the clock's x position")
    parser.add_argument("-y", type=int, default=None, help="Set the clock's y position")
    parser.add_argument(
        "-D", "--delay", type=float, default=None, help="Set the update delay (seconds)"
    )
    parser.add_argument(
        "-S",
        "--save-config",
        action="store_true",
        help="Save current settings to config file",
    )

    return vars(parser.parse_args())


def apply_cli_args(base_config: dict[str, Any], args: dict[str, Any]) -> dict[str, Any]:
    """Apply command line arguments to base configuration."""
    config = base_config.copy()

    # Update display options
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
    if args["screensaver"]:
        config["options"]["screensaver"] = True
        # Screensaver implies center is off (we control position)
        config["options"]["center"] = False
    if args["random_color"]:
        config["options"]["random_color"] = True

    # Update color
    if args["color"] is not None:
        color_names = [c.name for c in Color]
        config["color"] = color_names[args["color"]]

    # Update font
    if args["font"] is not None:
        config["font"] = args["font"]

    # Update delay
    if args["delay"] is not None:
        config["delay"] = args["delay"]

    # Update position
    if args["x"] is not None:
        config["position"]["x"] = args["x"]
    if args["y"] is not None:
        config["position"]["y"] = args["y"]

    return config


def setup_terminal(stdscr: Any) -> None:
    """Initialize terminal settings for curses."""
    curses.curs_set(0)  # Hide cursor
    curses.start_color()
    curses.use_default_colors()

    # Initialize color pairs
    for color in Color:
        curses.init_pair(color.value + 1, color.value, -1)

    stdscr.clear()
    stdscr.nodelay(True)  # Non-blocking input


def run_clock(stdscr: Any, clock: Clock, renderer: ClockRenderer, config: Any, delay: float) -> None:
    """Main clock display loop."""
    setup_terminal(stdscr)
    last_time_str: str | None = None
    last_date_str: str | None = None
    last_size: tuple[int, int] | None = None
    force_redraw = False

    # Initialize screensaver if enabled
    screensaver = None
    if DisplayOption.SCREENSAVER in config.options:
        screensaver = Screensaver(config)
        max_y, max_x = stdscr.getmaxyx()
        screensaver.reset_position(max_x, max_y)

    while True:
        # Check for quit key
        try:
            key = stdscr.getch()
            if key in (ord("q"), ord("Q"), 27):  # q, Q, or ESC
                break
            elif key == curses.KEY_RESIZE:
                force_redraw = True
        except curses.error:
            pass

        # Get current terminal size
        current_size = stdscr.getmaxyx()

        # Detect size change
        if last_size != current_size:
            force_redraw = True
            last_size = current_size
            stdscr.clear()  # Clear screen on resize
            if screensaver:
                screensaver.reset_position(current_size[1], current_size[0])

        # Update display if needed
        if clock.should_update() or force_redraw or screensaver:
            time_str, date_str = clock.get_display_strings()

            # Redraw if changed or forced or in screensaver mode
            if time_str != last_time_str or date_str != last_date_str or force_redraw or screensaver:
                max_y, max_x = stdscr.getmaxyx()
                stdscr.erase()  # Clear previous content

                # Get screensaver position and color if enabled
                override_pos = None
                override_color = None
                if screensaver:
                    # Calculate display dimensions for screensaver
                    width, height = renderer._get_display_dimensions(time_str, date_str)
                    override_pos = screensaver.update_position(width, height, max_x, max_y)
                    current_color = screensaver.get_color()
                    override_color = current_color.value + 1

                renderer.render(stdscr, max_y, max_x, time_str, date_str, override_pos, override_color)
                stdscr.refresh()
                last_time_str = time_str
                last_date_str = date_str
                force_redraw = False

        time.sleep(delay)


def main() -> None:
    """Main entry point."""
    args = parse_arguments()

    # Load and apply configuration
    base_config = load_config()
    config_dict = apply_cli_args(base_config, args)

    # Save config if requested
    if args["save_config"]:
        save_config(config_dict)
        print(f"Configuration saved to {load_config.__module__}")
        # Exit if no display options were given
        if not any(
            args[opt]
            for opt in [
                "center",
                "seconds",
                "bold",
                "twelve",
                "blink",
                "utc",
                "date",
                "ampm",
                "color",
                "x",
                "y",
                "delay",
            ]
        ):
            return

    # Create clock and renderer
    clock_config = dict_to_clock_config(config_dict)
    clock = Clock(clock_config)
    renderer = ClockRenderer(clock_config)

    # Run the display
    try:
        curses.wrapper(lambda stdscr: run_clock(stdscr, clock, renderer, clock_config, clock_config.delay))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
