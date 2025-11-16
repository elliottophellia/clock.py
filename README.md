# ttyclock-py

A Python implementation of the classic [tty-clock](https://github.com/xorg62/tty-clock), a digital clock for your terminal.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square) ![License](https://img.shields.io/badge/License-CC--BY--SA--4.0-green?style=flat-square) ![Version](https://img.shields.io/badge/Version-2.0.0-orange?style=flat-square)

[![Buy Me a Coffee](https://img.shields.io/badge/BUY%20ME%20A%20COFFEE-79B8CA?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/ReidhoSatria) [![Traktir Saya Kopi](https://img.shields.io/badge/TRAKTIR%20SAYA%20KOPI-FAC76C?style=for-the-badge&logo=BuyMeACoffee&logoColor=black)](https://saweria.co/elliottophellia)

## What's new in v2.0.0 ?!

Major rewrite. Here's what changed:

**Tooling:**
- Poetry → uv
- Python 3.8+ → 3.10+
- Added mypy (strict type checking)
- Added ruff (linter)
- Reorganized from `src/clock/py/` to `src/ttyclock/`

**Code:**
- Split into modules instead of one big file
- Full type hints
- Better architecture

**Features:**
- 5 fonts (was 1)
- Screensaver mode
- Random colors
- Better date format (now shows day of week)
- Terminal resize handling
- Centered error messages

**Breaking:**
- Needs Python 3.10+
- Module path changed (but CLI is same)

All CLI arguments work the same. Config format is backwards compatible.

## Install

```bash
pip install ttyclock-py
```

Build from source:

```bash
git clone https://github.com/elliottophellia/clock.py
cd clock.py
uv build
pipx install dist/ttyclock_py-2.0.0-py3-none-any.whl
```

## Usage

```bash
ttyclock-py              # basic
ttyclock-py -c -s        # centered with seconds
ttyclock-py -t -P -d     # 12-hour + AM/PM + date
ttyclock-py -r -R        # screensaver mode with random colors
```

## Options

```
-c, --center          center it
-s, --seconds         show seconds
-b, --bold            bold text
-t, --twelve          12-hour format
-P, --ampm            show AM/PM (needs -t)
-k, --blink           blink the colon
-u, --utc             use UTC
-d, --date            show date
-r, --screensaver     bouncing screensaver (like DVD logo)
-R, --random-color    random colors when bouncing
-C N                  color (0-7): black/red/green/yellow/blue/magenta/cyan/white
-f FONT               font: block/slim/dot/bold/mini
-x X, -y Y            position
-D DELAY              update delay in seconds (default 0.1)
-S, --save-config     save settings
```

Quit with `q`, `Q`, or `ESC`.

## Fonts

5 fonts available:

- `block` - default
- `slim` - narrower
- `dot` - retro LED look
- `bold` - thick
- `mini` - compact

Try them: `ttyclock-py -f dot -c`

## Screensaver

`-r` makes it bounce around. Add `-R` for color changes.

```bash
ttyclock-py -r -R -s -d
```

## Config

Config location:
- Linux/macOS: `~/.config/ttyclock-py/config.json`
- Windows: `%LOCALAPPDATA%\ttyclock-py\config.json`

```json
{
  "color": "GREEN",
  "font": "block",
  "delay": 0.1,
  "options": {
    "twelve_hour": false,
    "show_seconds": true,
    "bold": false,
    "center": true,
    "blink_colon": false,
    "utc": false,
    "show_date": true,
    "show_ampm": false,
    "screensaver": false,
    "random_color": false
  },
  "position": {"x": 0, "y": 0}
}
```

Use `-S` to save current settings or edit the file directly.

## Dev

```bash
git clone https://github.com/elliottophellia/clock.py
cd clock.py
uv sync
uv run ttyclock-py

# checks
uv run ruff check src/ttyclock
uv run mypy src/ttyclock

# build
uv build
```

Code is in `src/ttyclock/`:
- `types.py` - enums/dataclasses
- `fonts.py` - font data
- `digits.py` - pattern lookup
- `time_formatter.py` - time/date strings
- `clock.py` - state
- `renderer.py` - drawing
- `screensaver.py` - bouncing
- `config.py` - file I/O
- `__main__.py` - CLI

## License

This project is licensed under the Creative Commons Attribution Share Alike 4.0 International (CC-BY-SA-4.0). For more information, please refer to the [LICENSE](LICENSE) file included in this repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Write your amazing code
4. Make sure pass `ruff check` and `mypy` first
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`) 
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request