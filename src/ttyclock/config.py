"""Configuration file management."""

import copy
import json
import sys
from pathlib import Path
from typing import Any

from .types import ClockConfig, Color, DisplayOption, Position


def _get_config_dir() -> Path:
    """Get platform-specific config directory."""
    if sys.platform == "win32":
        # Windows: use AppData/Local
        appdata = Path.home() / "AppData" / "Local"
        return appdata / "ttyclock-py"
    else:
        # Unix-like: use XDG config
        return Path.home() / ".config" / "ttyclock-py"


CONFIG_DIR = _get_config_dir()
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "color": "GREEN",
    "delay": 0.1,
    "font": "block",
    "options": {
        "twelve_hour": False,
        "show_seconds": False,
        "bold": False,
        "center": False,
        "blink_colon": False,
        "utc": False,
        "show_date": False,
        "show_ampm": False,
        "screensaver": False,
        "random_color": False,
    },
    "position": {"x": 0, "y": 0},
}


def ensure_config_dir() -> None:
    """Ensure configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load configuration from file or return defaults."""
    if not CONFIG_FILE.exists():
        ensure_config_dir()
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with CONFIG_FILE.open() as f:
            config_data = json.load(f)
        return _merge_with_defaults(config_data)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CONFIG


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    with CONFIG_FILE.open("w") as f:
        json.dump(config, f, indent=4)


def _merge_with_defaults(config: dict[str, Any]) -> dict[str, Any]:
    """Merge loaded config with defaults to ensure all fields exist."""
    result = copy.deepcopy(DEFAULT_CONFIG)

    # Update color
    if "color" in config and isinstance(config["color"], str):
        result["color"] = config["color"]

    # Update delay
    if "delay" in config and isinstance(config["delay"], (int, float)):
        result["delay"] = float(config["delay"])

    # Update font
    if "font" in config and isinstance(config["font"], str):
        result["font"] = config["font"]

    # Update options
    if "options" in config and isinstance(config["options"], dict):
        options_dict = result["options"]
        assert isinstance(options_dict, dict)
        for key, value in config["options"].items():
            if key in options_dict and isinstance(value, bool):
                options_dict[key] = value

    # Update position
    if "position" in config and isinstance(config["position"], dict):
        position_dict = result["position"]
        assert isinstance(position_dict, dict)
        for key, value in config["position"].items():
            if key in position_dict and isinstance(value, int):
                position_dict[key] = value

    return result


def dict_to_clock_config(config: dict[str, Any]) -> ClockConfig:
    """Convert dictionary config to ClockConfig object."""
    # Parse color
    color_name = config.get("color", "GREEN")
    color = Color[color_name] if color_name in Color.__members__ else Color.GREEN

    # Parse delay
    delay = float(config.get("delay", 0.1))

    # Parse font
    font = config.get("font", "block")

    # Parse options
    options = []
    opt_dict = config.get("options", {})

    if opt_dict.get("twelve_hour"):
        options.append(DisplayOption.TWELVE_HOUR)
    if opt_dict.get("show_seconds"):
        options.append(DisplayOption.SHOW_SECONDS)
    if opt_dict.get("bold"):
        options.append(DisplayOption.BOLD)
    if opt_dict.get("center"):
        options.append(DisplayOption.CENTER)
    if opt_dict.get("blink_colon"):
        options.append(DisplayOption.BLINK_COLON)
    if opt_dict.get("utc"):
        options.append(DisplayOption.UTC)
    if opt_dict.get("show_date"):
        options.append(DisplayOption.SHOW_DATE)
    if opt_dict.get("show_ampm"):
        options.append(DisplayOption.SHOW_AMPM)
    if opt_dict.get("screensaver"):
        options.append(DisplayOption.SCREENSAVER)
    if opt_dict.get("random_color"):
        options.append(DisplayOption.RANDOM_COLOR)

    # Parse position
    pos_dict = config.get("position", {})
    position = Position(x=pos_dict.get("x", 0), y=pos_dict.get("y", 0))

    return ClockConfig(color=color, delay=delay, options=options, position=position, font=font)


def clock_config_to_dict(config: ClockConfig) -> dict[str, Any]:
    """Convert ClockConfig object to dictionary."""
    return {
        "color": config.color.name,
        "delay": config.delay,
        "font": config.font,
        "options": {
            "twelve_hour": DisplayOption.TWELVE_HOUR in config.options,
            "show_seconds": DisplayOption.SHOW_SECONDS in config.options,
            "bold": DisplayOption.BOLD in config.options,
            "center": DisplayOption.CENTER in config.options,
            "blink_colon": DisplayOption.BLINK_COLON in config.options,
            "utc": DisplayOption.UTC in config.options,
            "show_date": DisplayOption.SHOW_DATE in config.options,
            "show_ampm": DisplayOption.SHOW_AMPM in config.options,
            "screensaver": DisplayOption.SCREENSAVER in config.options,
            "random_color": DisplayOption.RANDOM_COLOR in config.options,
        },
        "position": {"x": config.position.x, "y": config.position.y},
    }
