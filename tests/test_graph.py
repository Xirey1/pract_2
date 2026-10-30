"""Проверки рекурсивного BFS и валидации JSON."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from graph import TestRepository, build_graph

ROOT = Path(__file__).resolve().parents[1]


class GraphTests(unittest.TestCase):
    """Цепочка, ромб, цикл, петля и изолированный пакет."""

    def graph(self, name):
        """Прочитать пример и обойти его от A."""
        return build_graph("A", TestRepository(ROOT / "examples" / name))

    def test_bfs_order_and_shared_dependency(self):
        """Открывать узлы по слоям и один раз для общего потомка."""
        graph = self.graph("diamond.json")
        self.assertEqual(list(graph), ["A", "B", "C", "D"])
        self.assertEqual(graph["B"], graph["C"])
        self.assertNotIn("Z", graph)

    def test_cycles_terminate(self):
        """Сохранить обратное ребро, завершив обход."""
        graph = self.graph("cycle.json")
        self.assertEqual(list(graph), ["A", "B", "C", "D"])
        self.assertEqual(graph["C"], ["A", "D"])
        self.assertEqual(self.graph("self_cycle.json"), {"A": ["A"]})

    def test_chain_and_isolated(self):
        """Обработать цепочку и граф без ребер."""
        self.assertEqual(list(self.graph("chain.json")), ["A", "B", "C"])
        self.assertEqual(self.graph("isolated.json"), {"A": []})

    def test_invalid_repositories(self):
        """Отклонить неверный JSON, имена и ссылки."""
        cases = ["bad", "[]", "{}", '{"a": []}', '{"A": "B"}',
                 '{"A": ["B"]}', '{"A": [1]}', '{"A": ["A", "A"]}']
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "repo.json"
            for content in cases:
                path.write_text(content, encoding="utf-8")
                with self.subTest(content=content):
                    with self.assertRaises(ValueError):
                        TestRepository(path)

    def test_unknown_package(self):
        """Не возвращать пустой список для отсутствующего пакета."""
        repo = TestRepository(ROOT / "examples" / "isolated.json")
        with self.assertRaises(ValueError):
            repo.direct("B")
