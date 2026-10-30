"""Точка входа приложения."""

from config import format_config, parse_args
from maven import MavenRepository
from graph import TestRepository, build_graph
from operations import loading_order
from render import ascii_tree, mermaid
import sys


def main(argv=None):
    """Запустить CLI и вернуть код завершения."""
    args = parse_args(argv)
    try:
        if args.mode == "config":
            print(format_config(args))
        else:
            repository_class = (TestRepository if args.test_repository
                                else MavenRepository)
            repository = repository_class(args.repository)
            if args.mode == "direct":
                dependencies = repository.direct(args.package, include_all=True)
                print("\n".join(dependencies) or "Прямых зависимостей нет")
            else:
                graph = build_graph(args.package, repository)
                if args.mode == "order":
                    print("\n".join(loading_order(graph)))
                else:
                    print(mermaid(graph))
                    if args.ascii_tree:
                        print("\n" + ascii_tree(graph, args.package))
    except RecursionError:
        print("Ошибка: превышена глубина рекурсивного BFS", file=sys.stderr)
        return 1
    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
