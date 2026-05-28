import sys
from . import config, api, icons, notify


def main():
    argv = sys.argv[1:]

    if not argv:
        _do_current()
    elif argv[0] == 'set-location':
        if len(argv) != 3:
            print("Usage: wxnotify set-location <lat> <lon>", file=sys.stderr)
            sys.exit(1)
        config.set_location(argv[1], argv[2])
    elif argv[0] == 'set-apikey':
        if len(argv) != 2:
            print("Usage: wxnotify set-apikey <key>", file=sys.stderr)
            sys.exit(1)
        config.set_apikey(argv[1])
    elif argv[0] == 'set-units':
        if len(argv) != 2:
            print("Usage: wxnotify set-units <imperial|metric>", file=sys.stderr)
            sys.exit(1)
        config.set_units(argv[1])
    elif argv[0] == 'show-config':
        config.show_config()
    else:
        try:
            hours = int(argv[0])
        except ValueError:
            print(f"Unknown command: {argv[0]}", file=sys.stderr)
            sys.exit(1)
        if hours < 0:
            print("Error: hours must be non-negative", file=sys.stderr)
            sys.exit(1)
        _do_forecast(hours)


def _do_current():
    cfg = config.load_config()
    data = api.fetch_current(cfg)
    icon_path = icons.get_icon_path(data.get('weather', [{}])[0].get('icon'))
    title = 'Wx-notify'
    body = notify.format_body(data, is_forecast=False, units=cfg['units'])
    notify.send_notification(title, body, icon_path)


def _do_forecast(hours):
    cfg = config.load_config()
    data = api.fetch_forecast(cfg, hours)
    icon_path = icons.get_icon_path(data.get('weather', [{}])[0].get('icon'))
    title = 'Wx-notify -- Forecast'
    body = notify.format_body(data, is_forecast=True, units=cfg['units'])
    notify.send_notification(title, body, icon_path)


if __name__ == '__main__':
    main()
