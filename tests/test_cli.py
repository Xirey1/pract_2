"""Интеграционные проверки CLI с настоящими локальными файлами."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    """Проверить stdout, stderr и коды завершения процесса."""

    def run_cli(self, name="diamond", *extra):
        """Вызвать программу в отдельном процессе."""
        command = [sys.executable, "-X", "utf8", "src/main.py",
                   "--package", "A", "--repository", f"examples/{name}.json",
                   "--test-repository", *extra]
        return subprocess.run(command, cwd=ROOT, capture_output=True,
                              encoding="utf-8", timeout=10)

    def test_graph_output(self):
        """Вывести обе формы визуализации."""
        result = self.run_cli("diamond", "--ascii")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("flowchart TD"))
        self.assertIn("[shared]", result.stdout)

    def test_direct_and_order(self):
        """Режимы не должны добавлять служебный текст в stdout."""
        result = self.run_cli("diamond", "--mode", "direct")
        self.assertEqual(result.stdout.strip().splitlines(), ["B", "C"])
        result = self.run_cli("chain", "--mode", "order")
        self.assertEqual(result.stdout.strip().splitlines(), ["C", "B", "A"])

    def test_cycle_error(self):
        """При цикле вернуть код 1 и объяснение в stderr."""
        result = self.run_cli("cycle", "--mode", "order")
        self.assertEqual(result.returncode, 1)
        self.assertIn("цикл", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_incompatible_option(self):
        """Нельзя молча игнорировать ASCII в режиме порядка."""
        result = self.run_cli("chain", "--mode", "order", "--ascii")
        self.assertEqual(result.returncode, 2)
