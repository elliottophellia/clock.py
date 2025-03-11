# Clock.py

A Python implementation of the classic tty-clock, a digital clock for your terminal.


![Python](https://img.shields.io/badge/PYTHON-3.X-bf616a?style=flat-square) ![License](https://img.shields.io/badge/LICENCE-CC%20BY%20SA%204.0-ebcb8b?style=flat-square) ![Version](https://img.shields.io/badge/VERSION-1.0.0-a3be8c?style=flat-square)

[![Buy Me a Coffee](https://img.shields.io/badge/BUY%20ME%20A%20COFFEE-79B8CA?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/ReidhoSatria) [![Traktir Saya Kopi](https://img.shields.io/badge/TRAKTIR%20SAYA%20KOPI-FAC76C?style=for-the-badge&logo=BuyMeACoffee&logoColor=black)](https://saweria.co/elliottophellia)

## Features

- 12/24 hour mode
- Show/hide seconds
- Display date
- Custom colors
- Blink separator
- UTC time mode
- Centered or custom positioning
- Bold characters

## Installation

### Release

```bash
# Install using pipx
pipx install ttyclock-py
```

### Build from Source

```bash
# Clone the repository
git clone https://github.com/elliottophellia/clock.py

# Change directory
cd clock.py

# Build the package
poetry build

# Install the package
pipx install dist/ttyclock_py-1.0.0.tar.gz
```

## Usage

```bash
ttyclock-py
```

### Command Line Options

```
-h, --help            show this help message and exit
-c, --center          Center the clock in the terminal
-s, --seconds         Show seconds in the clock
-b, --bold            Use bold characters
-t, --twelve          Use 12-hour format
-P, --ampm            Show AM/PM indicator in 12-hour format
-k, --blink           Blink the colon
-u, --utc             Use UTC time
-d, --date            Show current date
-C, --color {0,1,2,3,4,5,6,7}
                      Set the clock color (0-7)
-x X                  Set the clock's x position
-y Y                  Set the clock's y position
-D, --delay DELAY     Set the update delay (seconds)
-S, --save-config     Save current settings to config file
```

## Configuration

The program stores its configuration in `~/.config/clock-py/config.json`. You can modify this file directly or use the `--save-config` option to save your current settings.

Default configuration:
```json
{
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
```

## License

This project is licensed under the Creative Commons Attribution Share Alike 4.0 International (CC-BY-SA-4.0). For more information, please refer to the [LICENSE](LICENSE) file included in this repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
