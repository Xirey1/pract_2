"""Операции над построенным графом зависимостей."""

from collections import deque


def loading_order(graph):
    """Алгоритм Кана: зависимости раньше зависимых пакетов."""
    remaining = {node: len(dependencies)
                 for node, dependencies in graph.items()}
    dependents = {node: [] for node in graph}
    for node, dependencies in graph.items():
        for dependency in dependencies:
            dependents[dependency].append(node)
    ready = deque(node for node, count in remaining.items() if count == 0)
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for dependent in dependents[node]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                ready.append(dependent)
    if len(order) != len(graph):
        blocked = ", ".join(node for node, count in remaining.items() if count)
        raise ValueError(
            "Порядок загрузки невозможен: обнаружен цикл. "
            f"Не удалось упорядочить: {blocked}"
        )
    return order
