"""Проверки корректности порядка загрузки."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from graph import TestRepository, build_graph
from operations import loading_order

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class OrderTests(unittest.TestCase):
    """Проверять порядок по каждому ребру и отклонять циклы."""

    def test_dependency_precedes_dependent(self):
        """Для любого ребра A->B индекс B должен быть меньше индекса A."""
        for name in ["chain.json", "diamond.json", "isolated.json"]:
            graph = build_graph("A", TestRepository(EXAMPLES / name))
            order = loading_order(graph)
            with self.subTest(name=name):
                self.assertEqual(set(order), set(graph))
                self.assertEqual(len(order), len(set(order)))
                for node, dependencies in graph.items():
                    for dependency in dependencies:
                        self.assertLess(order.index(dependency), order.index(node))

    def test_cycles_have_no_order(self):
        """Цикл и петля не имеют топологического порядка."""
        for name in ["cycle.json", "self_cycle.json"]:
            graph = build_graph("A", TestRepository(EXAMPLES / name))
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "цикл"):
                    loading_order(graph)
