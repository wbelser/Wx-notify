# Wx-notify

Desktop weather notifications via the [OpenWeatherMap API](https://openweathermap.org/api)
and Linux `notify-send`. Fetches current conditions or a 5-day/3-hour forecast
and displays them as a standard desktop notification with weather icons.

Zero external Python dependencies -- only the standard library is used.

## Project Layout

```
Wx-notify/
  pyproject.toml          # Build configuration, entry point
  LICENSE                 # GPLv3
  README.md
  src/
    wxnotify/
      __init__.py         # Package marker (empty)
      __main__.py         # CLI dispatch, main() entry point
      config.py           # Config file read/write at ~/.config/wxnotify/
      api.py              # OpenWeatherMap HTTP calls (current + forecast)
      icons.py            # Icon download + cache at ~/.cache/wxnotify/icons/
      notify.py           # Body formatting, notify-send dispatch, compass
```

## Prerequisites

- **Python 3.9+**
- **notify-send** -- the `libnotify` desktop notification daemon.
  Install with your package manager:

  | Distro       | Package          |
  |--------------|------------------|
  | Debian/Ubuntu| `libnotify-bin`  |
  | Fedora       | `libnotify`      |
  | Arch Linux   | `libnotify`      |

- **OpenWeatherMap API key** -- free tier available at
  [openweathermap.org](https://openweathermap.org/appid).

## Installation

### Via pipx (recommended)

```bash
pipx install git+https://github.com/wbelser/Wx-notify.git
```

This creates an isolated virtual environment and exposes the `wxnotify` command
on your `$PATH`.

### From a local clone

```bash
git clone https://github.com/wbelser/Wx-notify.git
cd Wx-notify
pipx install .
```

Or with regular pip inside a virtual environment of your choice:

```bash
python3 -m venv venv
source venv/bin/activate
pip install .
```

### Run without installing

```bash
python3 -m src.wxnotify
```

(Requires the working directory to be the repository root.)

## Setup

Before displaying weather, you need to configure your API key and location.

### 1. Set your API key

```bash
wxnotify set-apikey YOUR_OPENWEATHERMAP_API_KEY
```

The key is stored in `~/.config/wxnotify/config.json` (or
`$XDG_CONFIG_HOME/wxnotify/config.json` if set).

### 2. Set your location

```bash
wxnotify set-location 41.66 -93.60
```

Accepts latitude and longitude as decimal degrees.

### 3. Choose units (optional)

```bash
wxnotify set-units imperial     # Fahrenheit, mph (default if not set)
wxnotify set-units metric       # Celsius, m/s
```

### 4. Verify configuration

```bash
wxnotify show-config
```

Example output:

```
appid: 12ab****
lat: 41.66
lon: -93.60
units: imperial
```

The API key is masked to show only the first four characters.

## Usage

### Current conditions

```bash
wxnotify
```

Displays a desktop notification with current temperature, feels-like,
high/low, weather description, wind (speed, direction, gusts), humidity,
and barometric pressure.

### Forecast

```bash
wxnotify 24       # Forecast 24 hours from now
wxnotify 48       # Forecast 48 hours from now
wxnotify 72       # Forecast 72 hours from now
```

The argument is a number of hours in the future (0 to 120, the 5-day
forecast window). The tool selects the forecast entry closest to the
requested time and displays it with the same layout -- additionally
including a precipitation probability ("Rain") line.

Example notification body:

```
Brooklyn
now (02:34 PM)

72.5 F (feels like 68.3 F)
High: 78.1 F  Low: 65.2 F
overcast clouds
Wind: 12.3 mph SW (gusts 18.7 mph)
Humidity: 54%  Pressure: 1015 hPa
```

Forecast variant adds the date/time and rain probability:

```
Brooklyn
May 28, 02:00 PM

72.5 F (feels like 68.3 F)
High: 78.1 F  Low: 65.2 F
overcast clouds
Wind: 12.3 mph SW (gusts 18.7 mph)
Humidity: 54%  Pressure: 1015 hPa
Rain: 40%
```

## Helper Commands

| Command                           | Description                            |
|-----------------------------------|----------------------------------------|
| `wxnotify show-config`            | Print current config (API key masked)  |
| `wxnotify set-apikey <key>`       | Save OpenWeatherMap API key            |
| `wxnotify set-location <lat> <lon>`| Save latitude and longitude           |
| `wxnotify set-units <imperial|metric>`| Save unit preference              |

### Files and Paths

| Purpose        | Default Location                      | Override                     |
|----------------|---------------------------------------|------------------------------|
| Config JSON    | `~/.config/wxnotify/config.json`      | `$XDG_CONFIG_HOME`           |
| Icon cache     | `~/.cache/wxnotify/icons/`            | `$XDG_CACHE_HOME`            |

Icons are downloaded once from OpenWeatherMap and cached indefinitely by
icon code (e.g. `10d@2x.png`).

## Wind Compass

Wind direction is displayed as a 16-point compass bearing:

```
N, NNE, NE, ENE, E, ESE, SE, SSE,
S, SSW, SW, WSW, W, WNW, NW, NNW
```

Derived by rounding degrees and indexing the 16-point table.

## Under the Hood

- **config.py** -- reads/writes `~/.config/wxnotify/config.json` with atomic
  save (write to temp file, then rename). Validates required keys and unit
  values on load.
- **api.py** -- uses `urllib.request` to call `/data/2.5/weather` (current) or
  `/data/2.5/forecast` (5-day/3-hour). Forecast selects the entry nearest the
  requested timestamp and validates it falls within the available window.
- **icons.py** -- downloads `{code}@2x.png` from OpenWeatherMap's CDN and
  caches it in `~/.cache/wxnotify/icons/`. Returns `None` on failure instead
  of crashing.
- **notify.py** -- builds the notification body string, computes compass
  direction, and dispatches via `subprocess.run(['notify-send', ...])` with
  a 10-second timeout and application name `wxnotify`.
- **__main__.py** -- parses `sys.argv`, dispatches to sub-commands, and glues
  config/api/icons/notify together for current and forecast flows.

## License

GPLv3 -- see [LICENSE](LICENSE).
