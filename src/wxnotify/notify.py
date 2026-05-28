import subprocess
import sys
from datetime import datetime


_DIRS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
         'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']


def compass(deg):
    idx = round(deg / 22.5) % 16
    return _DIRS[idx]


def _city_label(data):
    name = (data.get('name') or '').strip()
    if name:
        return name
    city_obj = data.get('city') or {}
    name = (city_obj.get('name') or '').strip()
    if name:
        return name
    coord = data.get('coord') or {}
    lat = coord.get('lat', '?')
    lon = coord.get('lon', '?')
    return f'{lat}, {lon}'


def format_body(data, is_forecast, units):
    lines = []

    if is_forecast:
        dt_txt = data.get('dt_txt', '')
        if dt_txt:
            dt = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S')
            time_str = dt.strftime('%b %d, %I:%M %p').lstrip('0').replace(' 0', ' ')
        else:
            time_str = ''
        lines.append(_city_label(data))
        lines.append(time_str)
    else:
        now = datetime.now()
        time_str = now.strftime('%I:%M %p').lstrip('0').replace(' 0', ' ')
        lines.append(_city_label(data))
        lines.append(f'now ({time_str})')

    lines.append('')

    main = data.get('main', {})
    temp = main.get('temp')
    feels_like = main.get('feels_like')
    temp_max = main.get('temp_max')
    temp_min = main.get('temp_min')

    temp_unit = 'F' if units == 'imperial' else 'C'

    temp_line = f'{temp:.1f} {temp_unit} (feels like {feels_like:.1f} {temp_unit})'
    lines.append(temp_line)

    high_low = f'High: {temp_max:.1f} {temp_unit}  Low: {temp_min:.1f} {temp_unit}'
    lines.append(high_low)

    weather = data.get('weather', [{}])[0]
    description = weather.get('description', '')
    lines.append(description)

    wind = data.get('wind', {})
    speed = wind.get('speed', 0)
    deg = wind.get('deg', 0)
    gust = wind.get('gust')

    speed_unit = 'mph' if units == 'imperial' else 'm/s'
    wind_dir = compass(deg)

    if gust is not None:
        wind_line = f'Wind: {speed:.1f} {speed_unit} {wind_dir} (gusts {gust:.1f} {speed_unit})'
    else:
        wind_line = f'Wind: {speed:.1f} {speed_unit} {wind_dir}'
    lines.append(wind_line)

    humidity = main.get('humidity', 0)
    pressure = main.get('pressure', 0)
    lines.append(f'Humidity: {humidity}%  Pressure: {pressure} hPa')

    if is_forecast:
        pop = data.get('pop', 0)
        lines.append(f'Rain: {pop:.0%}')

    return '\n'.join(lines)


def send_notification(title, body, icon_path):
    cmd = ['notify-send']
    if icon_path:
        cmd.extend(['-i', icon_path])
    cmd.extend(['-a', 'wxnotify', '-t', '10000', title, body])

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("Error: notify-send not found. Install libnotify-bin (Debian/Ubuntu) "
              "or libnotify (Fedora/Arch).", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        sys.exit(1)
