"""Сравнить ребра Mermaid с сохраненным настоящим Maven dependency:tree."""

import re

from real_examples import PACKAGES, ROOT

MAVEN_LINE = re.compile(
    r"^\[INFO\] (.*?)([\w.-]+):([\w.-]+):jar:([^: ]+):(compile|runtime)$"
)


def maven_edges(path, root):
    """Восстановить ребра по отступам ASCII-дерева Maven."""
    edges = set()
    stack = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = MAVEN_LINE.match(line)
        if not match:
            continue
        prefix, group, artifact, version, _ = match.groups()
        package = f"{group}:{artifact}:{version}"
        depth = len(prefix) // 3
        stack[depth] = package
        if depth > 1:
            edges.add((stack[depth - 1], package))
        elif package != root:
            raise ValueError(f"Неожиданный корень Maven: {package}")
    return edges


def mermaid_edges(path):
    """Восстановить координаты вершин из сохраненного Mermaid."""
    source = path.read_text(encoding="utf-8")
    nodes = dict(re.findall(r'(n\d+)\["([^"]+)"\]', source))
    return {(nodes[a], nodes[b]) for a, b in
            re.findall(r"(n\d+) --> (n\d+)", source)}


def main():
    """Проверить равенство ребер трех графов и наличие успешных логов."""
    for package in PACKAGES:
        artifact = package.split(":")[1]
        tree = ROOT / "docs/maven" / f"{artifact}.tree.txt"
        resolve = ROOT / "docs/maven" / f"{artifact}.resolve.txt"
        own = mermaid_edges(ROOT / "docs/examples" / f"{artifact}.mmd")
        actual = maven_edges(tree, package)
        assert own == actual, (package, own, actual)
        for path in [tree, resolve]:
            assert "BUILD SUCCESS" in path.read_text(encoding="utf-8"), path
        print(f"{package}: MATCH ({len(actual)} edges)")


if __name__ == "__main__":
    main()
