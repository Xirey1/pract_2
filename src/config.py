"""Проверка параметров командной строки."""

import argparse
import re
from pathlib import Path
from urllib.parse import urlsplit


def coordinates(value):
    """Проверить координаты groupId:artifactId:version."""
    parts = value.split(":")
    if len(parts) != 3 or not all(
        re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.+-]*", part)
        for part in parts
    ):
        raise ValueError("Ожидается пакет groupId:artifactId:version")
    if parts[2].endswith("-SNAPSHOT"):
        raise ValueError("SNAPSHOT-версии не поддерживаются")
    if any(part in {".", ".."} for part in parts):
        raise ValueError("Некорректные координаты пакета")
    return tuple(parts)


def parse_args(argv=None):
    """Прочитать и проверить все пользовательские настройки."""
    parser = argparse.ArgumentParser(
        description="ПР 2, вариант 11: зависимости Maven"
    )
    parser.add_argument("--package", required=True, help="G:A:V или A")
    parser.add_argument("--repository", required=True, help="URL или JSON")
    parser.add_argument("--test-repository", action="store_true")
    parser.add_argument("--ascii", action="store_true", dest="ascii_tree")
    parser.add_argument(
        "--mode", choices=["config", "direct", "graph", "order"],
        default="graph"
    )
    args = parser.parse_args(argv)
    try:
        validate(args)
    except ValueError as error:
        parser.error(str(error))
    return args


def validate(args):
    """Проверить согласованность имени пакета и репозитория."""
    if args.ascii_tree and args.mode not in {"config", "graph"}:
        raise ValueError("--ascii доступен только в режиме graph или config")
    if args.test_repository:
        if not re.fullmatch(r"[A-Z]+", args.package):
            raise ValueError("Тестовый пакет: только большие буквы A-Z")
        if not Path(args.repository).is_file():
            raise ValueError("Файл тестового репозитория не найден")
    else:
        coordinates(args.package)
        url = urlsplit(args.repository)
        if url.scheme not in {"http", "https"} or not url.hostname:
            raise ValueError(
                "Репозиторий должен иметь URL http:// или https://"
            )
        if url.query or url.fragment or url.username or url.password:
            raise ValueError(
                "URL не должен содержать query, fragment или пароль"
            )
        try:
            url.port
        except ValueError as error:
            raise ValueError("Некорректный порт репозитория") from error


def format_config(args):
    """Вернуть настройки в формате ключ=значение."""
    return "\n".join(f"{key}={value}" for key, value in vars(args).items())
