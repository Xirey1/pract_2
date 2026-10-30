"""Вывод графа на языке Mermaid и в виде ASCII-дерева."""


def mermaid(graph):
    """Описать все узлы и ребра с безопасными идентификаторами."""
    identifiers = {node: f"n{index}" for index, node in enumerate(graph)}
    lines = ["flowchart TD"]
    for node, identifier in identifiers.items():
        label = node.replace("&", "&amp;").replace('"', "&quot;")
        label = label.replace("<", "&lt;").replace(">", "&gt;")
        lines.append(f'    {identifier}["{label}"]')
    for node, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(
                f"    {identifiers[node]} --> {identifiers[dependency]}"
            )
    return "\n".join(lines)


def ascii_tree(graph, root):
    """Развернуть узел один раз, помечая циклы и общие зависимости."""
    lines = [root]
    expanded = {root}
    stack = []

    def push_children(node, prefix, path):
        """Поместить детей в стек в обратном порядке для печати слева."""
        children = graph[node]
        for index in range(len(children) - 1, -1, -1):
            stack.append((children[index], prefix,
                          index == len(children) - 1, path))

    push_children(root, "", frozenset({root}))
    while stack:
        node, prefix, last, path = stack.pop()
        connector = "`-- " if last else "|-- "
        suffix = ""
        if node in path:
            suffix = " [cycle]"
        elif node in expanded:
            suffix = " [shared]"
        lines.append(prefix + connector + node + suffix)
        if not suffix:
            expanded.add(node)
            child_prefix = prefix + ("    " if last else "|   ")
            push_children(node, child_prefix, path | {node})
    return "\n".join(lines)
