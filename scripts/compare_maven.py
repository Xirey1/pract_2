"""Отдельная проверка: Maven вызывается только для сравнения."""

import argparse
import os
import re
import subprocess
from pathlib import Path

from real_examples import PACKAGES, ROOT

PLUGIN = "org.apache.maven.plugins:maven-dependency-plugin:3.6.1"


def run(maven, package, goal):
    """Сохранить реальный вывод штатного инструмента Maven."""
    group, artifact, version = package.split(":")
    output = ROOT / "docs" / "maven"
    output.mkdir(parents=True, exist_ok=True)
    command = [maven, "-B", "-f",
               str(ROOT / "examples/maven-comparison/pom.xml"),
               f"{PLUGIN}:{goal}", "-Dscope=runtime",
               "-DincludeScope=runtime", f"-Dsample.group={group}",
               f"-Dsample.artifact={artifact}", f"-Dsample.version={version}",
               f"-Dmaven.repo.local={ROOT / 'tools/m2'}"]
    if goal == "tree":
        command.append("-ntp")
    env = dict(os.environ)
    env["MAVEN_OPTS"] = env.get("MAVEN_OPTS", "") + " -Dfile.encoding=UTF-8"
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                            encoding="utf-8", errors="replace", timeout=1800)
    # Абсолютные пути компьютера не нужны в публикуемом протоколе.
    log = (result.stdout + result.stderr).replace(str(ROOT), "<PROJECT>")
    log = re.sub(r"Total time:.*", "Total time: (omitted)", log)
    log = re.sub(r"Finished at:.*", "Finished at: (omitted)", log)
    (output / f"{artifact}.{goal}.txt").write_text(log, encoding="utf-8")
    print(f"{package} {goal}: exit {result.returncode}", flush=True)
    if result.returncode:
        raise RuntimeError(log[-5000:])


def main():
    """Запустить tree и resolve для трех выбранных пакетов."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maven", default="mvn")
    args = parser.parse_args()
    for package in PACKAGES:
        for goal in ["tree", "resolve"]:
            run(args.maven, package, goal)


if __name__ == "__main__":
    main()
