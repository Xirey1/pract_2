"""Операции над построенным графом зависимостей."""

from collections import deque


def reverse_edges(graph):
    """Сопоставить зависимости с пакетами, которым они нужны."""
    dependents = {node: [] for node in graph}
    for node, dependencies in graph.items():
        for dependency in dependencies:
            dependents[dependency].append(node)
    return dependents


def loading_order(graph):
    """Алгоритм Кана: зависимости раньше зависимых пакетов."""
    remaining = {node: len(dependencies)
                 for node, dependencies in graph.items()}
    dependents = reverse_edges(graph)
    ready = deque(node for node, count in remaining.items() if not count)
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for dependent in dependents[node]:
            remaining[dependent] -= 1
            if not remaining[dependent]:
                ready.append(dependent)
    if len(order) != len(graph):
        blocked = ", ".join(node for node, count in remaining.items() if count)
        raise ValueError(
            "Порядок загрузки невозможен: обнаружен цикл. "
            f"Не удалось упорядочить: {blocked}"
        )
    return order
