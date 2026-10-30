"""Тестовый репозиторий и построение графа рекурсивным BFS."""

import json
import re
from pathlib import Path


class TestRepository:
    """Локальный граф из JSON с именами A-Z."""

    def __init__(self, path):
        """Прочитать и проверить весь файл до обхода."""
        try:
            self.graph = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        except (ValueError, OSError) as error:
            raise ValueError(f"Не удалось прочитать JSON: {error}") from error
        if not isinstance(self.graph, dict) or not self.graph:
            raise ValueError("Репозиторий должен быть непустым JSON-объектом")
        for name, dependencies in self.graph.items():
            self.validate_node(name, dependencies)

    def validate_node(self, name, dependencies):
        """Проверить имя, список и существование всех зависимостей."""
        if not re.fullmatch(r"[A-Z]+", name):
            raise ValueError(f"Некорректное имя тестового пакета: {name}")
        if not isinstance(dependencies, list):
            raise ValueError(f"Зависимости {name} должны быть списком")
        for dependency in dependencies:
            if not isinstance(dependency, str) or dependency not in self.graph:
                raise ValueError(f"Неизвестная зависимость {name}: {dependency}")
        if len(dependencies) != len(set(dependencies)):
            raise ValueError(f"Повторяющиеся зависимости: {name}")

    def direct(self, package, include_all=False):
        """Получить прямые зависимости тестового пакета."""
        if package not in self.graph:
            raise ValueError(f"Пакет отсутствует в тестовом репозитории: {package}")
        return list(self.graph[package])


def build_graph(package, repository):
    """Обходить граф в ширину; рекурсивный вызов обрабатывает один слой."""
    graph = {}
    discovered = {package}

    def visit_level(frontier):
        """Обработать текущий слой и рекурсивно перейти к следующему."""
        if not frontier:
            return
        next_frontier = []
        for node in frontier:
            dependencies = repository.direct(node)
            graph[node] = dependencies
            for dependency in dependencies:
                if dependency not in discovered:
                    discovered.add(dependency)
                    next_frontier.append(dependency)
        visit_level(next_frontier)

    visit_level([package])
    return graph
