"""Проверки настроек CLI."""

import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import coordinates, format_config, parse_args


class ConfigTests(unittest.TestCase):
    """Корректные параметры и ошибки каждого параметра."""

    def test_valid(self):
        """Принять координаты и вывести все ключи."""
        args = parse_args([
            "--package", "org.example:demo:1.0",
            "--repository", "https://repo.maven.apache.org/maven2",
            "--ascii",
        ])
        self.assertIn("ascii_tree=True", format_config(args))
        self.assertEqual(coordinates(args.package)[1], "demo")

    def test_invalid(self):
        """Отклонить неверные и отсутствующие значения."""
        base = ["--package", "a:b:1", "--repository", "https://repo.test"]
        cases = [
            [], ["--package", "A"],
            ["--package", "bad", "--repository", "https://repo.test"],
            ["--package", "a:b:1", "--repository", "ftp://repo.test"],
            base + ["--ascii", "yes"],
            base + ["--test-repository", "yes"],
            base + ["--mode", "unknown"],
            base + ["--test-repository"],
        ]
        for argv in cases:
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    parse_args(argv)
                self.assertEqual(caught.exception.code, 2)
