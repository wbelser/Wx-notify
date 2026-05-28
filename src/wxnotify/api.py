import json
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "https://api.openweathermap.org"


def _request(url, params):
    query = '&'.join(f"{k}={v}" for k, v in params.items())
    full_url = f"{BASE_URL}{url}?{query}"
    try:
        resp = urllib.request.urlopen(full_url, timeout=10)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    return json.loads(resp.read().decode())


def geocode_by_zip(zip_code, country_code, appid):
    params = {
        'zip': f"{zip_code},{country_code}",
        'appid': appid,
    }
    return _request('/geo/1.0/zip', params)


def fetch_current(config):
    params = {
        'lat': config['lat'],
        'lon': config['lon'],
        'appid': config['appid'],
        'units': config['units'],
    }
    return _request('/data/2.5/weather', params)


def fetch_forecast(config, hours):
    params = {
        'lat': config['lat'],
        'lon': config['lon'],
        'appid': config['appid'],
        'units': config['units'],
    }
    data = _request('/data/2.5/forecast', params)
    entries = data.get('list', [])
    if not entries:
        print("Error: no forecast data available", file=sys.stderr)
        sys.exit(1)

    target = int(time.time()) + hours * 3600

    first_dt = entries[0]['dt']
    last_dt = entries[-1]['dt']
    if target < first_dt or target > last_dt:
        print(f"Error: requested {hours}h is outside the 5-day forecast window",
              file=sys.stderr)
        sys.exit(1)

    best = min(entries, key=lambda e: abs(e['dt'] - target))
    best['city'] = data.get('city', {})
    return best
