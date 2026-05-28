import json
import os
import sys
import shutil
import tempfile
from pathlib import Path

from . import api


def _config_dir():
    xdg = os.environ.get('XDG_CONFIG_HOME')
    if xdg:
        return Path(xdg) / 'wxnotify'
    return Path.home() / '.config' / 'wxnotify'


CONFIG_DIR = _config_dir()
CONFIG_PATH = CONFIG_DIR / 'config.json'


def load_config():
    if not CONFIG_PATH.exists():
        print("Error: config not found. Run 'wxnotify set-location <lat> <lon>' "
              "and 'wxnotify set-apikey <key>' first.", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(CONFIG_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        sys.exit(1)
    for key in ('appid', 'lat', 'lon', 'units'):
        if key not in data:
            print(f"Error: config missing '{key}'", file=sys.stderr)
            sys.exit(1)
    if data['units'] not in ('imperial', 'metric'):
        print("Error: units must be 'imperial' or 'metric'", file=sys.stderr)
        sys.exit(1)
    return data


def save_config(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir=CONFIG_DIR)
    try:
        json.dump(data, tmp, indent=2)
        tmp.write('\n')
        tmp.close()
        shutil.move(tmp.name, CONFIG_PATH)
    except OSError as e:
        os.unlink(tmp.name)
        print(f"Error saving config: {e}", file=sys.stderr)
        sys.exit(1)


def set_location(lat, lon):
    data = _load_or_create()
    data['lat'] = str(lat)
    data['lon'] = str(lon)
    save_config(data)


def set_location_by_zip(zip_code, country_code):
    data = _load_or_create()
    if 'appid' not in data:
        print("Error: API key not set. Run 'wxnotify set-apikey <key>' first.",
              file=sys.stderr)
        sys.exit(1)
    result = api.geocode_by_zip(zip_code, country_code, data['appid'])
    data['lat'] = str(result['lat'])
    data['lon'] = str(result['lon'])
    data['zip_code'] = zip_code
    data['zip_country'] = country_code
    save_config(data)


def set_apikey(key):
    data = _load_or_create()
    data['appid'] = key
    save_config(data)


def set_units(units):
    if units not in ('imperial', 'metric'):
        print("Error: units must be 'imperial' or 'metric'", file=sys.stderr)
        sys.exit(1)
    data = _load_or_create()
    data['units'] = units
    save_config(data)


def show_config():
    if not CONFIG_PATH.exists():
        print("Config not found at", CONFIG_PATH)
        sys.exit(0)
    try:
        data = json.loads(CONFIG_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        sys.exit(1)
    for key, value in data.items():
        if key == 'appid':
            value = value[:4] + '****' if len(value) > 4 else '****'
        print(f"{key}: {value}")


def _load_or_create():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error reading config: {e}", file=sys.stderr)
            sys.exit(1)
    return {}
