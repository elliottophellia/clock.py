"""Digit patterns for ASCII art clock display."""

from .fonts import get_font

DIGIT_HEIGHT = 6
DIGIT_SPACING = 1


def get_pattern(char: str, font: str = "block") -> list[str]:
    """Get the display pattern for a character using specified font."""
    font_data = get_font(font)
    return font_data.get(char, font_data.get(" ", ["     "] * DIGIT_HEIGHT))


def calculate_width(text: str, font: str = "block") -> int:
    """Calculate the total width needed to display text."""
    if not text:
        return 0

    total_width = 0
    for char in text:
        pattern = get_pattern(char, font)
        total_width += len(pattern[0]) + DIGIT_SPACING

    # Remove trailing space
    return total_width - DIGIT_SPACING if total_width > 0 else 0
