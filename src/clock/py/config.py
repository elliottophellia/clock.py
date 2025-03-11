import json
import os
from typing import Dict, Any

from .clock import ClockOption, ColorOption

# Default configuration path
DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/clock-py/config.json")

# Default configuration values
DEFAULT_CONFIG = {
    "color": "GREEN",
    "delay": 0.1,
    "options": {
        "twelve_hour": False,
        "show_seconds": False,
        "bold": False,
        "center": False,
        "blink_colon": False,
        "utc": False,
        "show_date": False,
        "show_ampm": False,
    },
    "position": {
        "x": 0,
        "y": 0
    }
}


def ensure_config_directory() -> None:
    """Ensure the configuration directory exists."""
    config_dir = os.path.dirname(DEFAULT_CONFIG_PATH)
    os.makedirs(config_dir, exist_ok=True)


def create_default_config() -> None:
    """Create a default configuration file if one doesn't exist."""
    ensure_config_directory()

    if not os.path.exists(DEFAULT_CONFIG_PATH):
        with open(DEFAULT_CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)


def load_config() -> Dict[str, Any]:
    """Load configuration from default file or create default if none exists."""
    # Create default config if it doesn't exist
    if not os.path.exists(DEFAULT_CONFIG_PATH):
        create_default_config()

    # Load configuration
    try:
        with open(DEFAULT_CONFIG_PATH, 'r') as f:
            config_data = json.load(f)

        # Validate and merge with defaults for any missing fields
        return merge_with_defaults(config_data)
    except (json.JSONDecodeError, IOError):
        # If there's an error loading the config, use the default
        return DEFAULT_CONFIG


def merge_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all required fields are present by merging with defaults."""
    result = DEFAULT_CONFIG.copy()

    # Update top-level fields
    if "color" in config and isinstance(config["color"], str):
        result["color"] = config["color"]

    if "delay" in config and isinstance(config["delay"], (int, float)):
        result["delay"] = float(config["delay"])

    # Update options
    if "options" in config and isinstance(config["options"], dict):
        for key, value in config["options"].items():
            if key in result["options"] and isinstance(value, bool):
                result["options"][key] = value

    # Update position
    if "position" in config and isinstance(config["position"], dict):
        for key, value in config["position"].items():
            if key in result["position"] and isinstance(value, int):
                result["position"][key] = value

    return result


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to default file."""
    ensure_config_directory()

    with open(DEFAULT_CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)


def config_to_options(config: Dict[str, Any]) -> Dict[str, Any]:
    """Convert configuration to options for the Clock class."""
    options = []

    # Convert options
    if config["options"]["twelve_hour"]:
        options.append(ClockOption.TWELVE_HOUR)
    if config["options"]["show_seconds"]:
        options.append(ClockOption.SECONDS)
    if config["options"]["bold"]:
        options.append(ClockOption.BOLD)
    if config["options"]["center"]:
        options.append(ClockOption.CENTER)
    if config["options"]["blink_colon"]:
        options.append(ClockOption.BLINK_COLON)
    if config["options"]["utc"]:
        options.append(ClockOption.UTC)
    if config["options"]["show_date"]:
        options.append(ClockOption.DATE)
    if config["options"]["show_ampm"]:
        options.append(ClockOption.AMPM)

    # Convert color
    color_map = {color.name: color for color in ColorOption}
    color = color_map.get(config["color"], ColorOption.GREEN)

    return {
        "color": color,
        "delay": config["delay"],
        "options": options,
        "x": config["position"]["x"],
        "y": config["position"]["y"]
    }
