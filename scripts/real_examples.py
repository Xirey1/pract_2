"""Воспроизвести три сетевых примера и сохранить результат в docs."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from graph import build_graph
from maven import MavenRepository
from operations import loading_order
from render import ascii_tree, mermaid

PACKAGES = [
    "junit:junit:4.13.2",
    "org.apache.commons:commons-text:1.12.0",
    "com.fasterxml.jackson.core:jackson-databind:2.17.2",
]


def write_gallery(output):
    """Собрать Markdown с диаграммами для просмотра на GitHub."""
    lines = ["# Примеры визуализации", "",
             "Получены из Maven Central для указанных версий.", ""]
    for package in PACKAGES:
        artifact = package.split(":")[1]
        lines.extend([f"## {package}", "", "```mermaid",
                      (output / f"{artifact}.mmd").read_text(encoding="utf-8"),
                      "```", "", "```text",
                      (output / f"{artifact}.txt").read_text(encoding="utf-8"),
                      "```", "", "Порядок загрузки:", "", "```text",
                      (output / f"{artifact}.order.txt").read_text(
                          encoding="utf-8"), "```", ""])
    (ROOT / "docs/EXAMPLES.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    """Скачать POM, построить графы и записать демонстрационные файлы."""
    output = ROOT / "docs" / "examples"
    output.mkdir(parents=True, exist_ok=True)
    repo = MavenRepository("https://repo.maven.apache.org/maven2")
    for package in PACKAGES:
        artifact = package.split(":")[1]
        graph = build_graph(package, repo)
        files = {
            "mmd": mermaid(graph),
            "txt": ascii_tree(graph, package),
            "order.txt": "\n".join(loading_order(graph)),
            "direct.txt": "\n".join(repo.direct(package, include_all=True)),
        }
        for extension, content in files.items():
            (output / f"{artifact}.{extension}").write_text(
                content + "\n", encoding="utf-8"
            )
        print(f"{package}: {len(graph)} nodes, "
              f"{sum(map(len, graph.values()))} edges", flush=True)
    write_gallery(output)


if __name__ == "__main__":
    main()
