"""Проверки визуализации без потери ребер и зацикливания."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from render import ascii_tree, mermaid


class RenderTests(unittest.TestCase):
    """Изолированные узлы, общие зависимости, циклы и экранирование."""

    def test_mermaid_all_edges(self):
        """Сохранить каждое ребро и отдельный лист."""
        graph = {"A": ["B", "C"], "B": ["C"], "C": [], "D": []}
        result = mermaid(graph)
        self.assertEqual(result.count(" --> "), 3)
        self.assertIn('n3["D"]', result)
        self.assertIn("n0 --> n1", result)
        self.assertIn("n1 --> n2", result)

    def test_ascii_shared(self):
        """Общую ветвь печатать с меткой shared."""
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        self.assertEqual(ascii_tree(graph, "A"),
                         "A\n|-- B\n|   `-- D\n`-- C\n    `-- D [shared]")

    def test_ascii_cycle(self):
        """Завершить цикл, явно сохранив обратное ребро."""
        self.assertEqual(ascii_tree({"A": ["A"]}, "A"),
                         "A\n`-- A [cycle]")

    def test_isolated_and_escape(self):
        """Показать одиночный узел и экранировать метку Mermaid."""
        self.assertEqual(ascii_tree({"A": []}, "A"), "A")
        self.assertIn("&quot;", mermaid({'A"B': []}))
