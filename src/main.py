"""Точка входа приложения."""

from config import format_config, parse_args
from maven import MavenRepository
import sys


def main(argv=None):
    """Запустить CLI и вернуть код завершения."""
    args = parse_args(argv)
    try:
        if args.mode == "config":
            print(format_config(args))
        elif args.test_repository:
            raise ValueError("Тестовый репозиторий появится на этапе 3")
        else:
            repository = MavenRepository(args.repository)
            dependencies = repository.direct(args.package, include_all=True)
            print("\n".join(dependencies) or "Прямых зависимостей нет")
    except (ValueError, OSError, RecursionError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
