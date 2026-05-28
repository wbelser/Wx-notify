import os
import urllib.request
import urllib.error
from pathlib import Path


def _cache_dir():
    xdg = os.environ.get('XDG_CACHE_HOME')
    if xdg:
        return Path(xdg) / 'wxnotify' / 'icons'
    return Path.home() / '.cache' / 'wxnotify' / 'icons'


CACHE_DIR = _cache_dir()
BASE_ICON_URL = "https://openweathermap.org/img/wn"


def get_icon_path(icon_code):
    if not icon_code:
        return None
    path = CACHE_DIR / f"{icon_code}.png"
    if path.exists():
        return str(path)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    url = f"{BASE_ICON_URL}/{icon_code}@2x.png"
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        path.write_bytes(resp.read())
        return str(path)
    except (urllib.error.URLError, OSError):
        return None
