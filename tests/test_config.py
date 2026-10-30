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
            with self.subTest(argv=argv):
                self.assert_invalid(argv)

    def assert_invalid(self, argv):
        """Проверить код ошибки, не выводя справку в журнал тестов."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                parse_args(argv)
            self.assertEqual(caught.exception.code, 2)

    def test_test_mode_and_invalid_values(self):
        """Проверить существующий JSON и разные неверные URL."""
        path = Path(__file__).resolve().parents[1] / "examples/chain.json"
        args = parse_args(["--package", "A", "--repository", str(path),
                           "--test-repository", "--mode", "config"])
        self.assertTrue(args.test_repository)
        for url in ["https://", "https://repo.test:bad", "file:///repo",
                    "https://repo.test/?q=a", "https://user:pw@repo.test"]:
            with self.subTest(url=url):
                self.assert_invalid(["--package", "g:a:1", "--repository", url])
        self.assert_invalid(["--package", "A", "--repository", "missing.json",
                             "--test-repository"])
