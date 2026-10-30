"""Точка входа приложения."""

from config import format_config, parse_args


def main(argv=None):
    """Запустить CLI и вернуть код завершения."""
    args = parse_args(argv)
    print(format_config(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
