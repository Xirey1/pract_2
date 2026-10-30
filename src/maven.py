"""Получение зависимостей из XML POM без менеджера пакетов."""

import re
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from xml.etree import ElementTree as ET

from config import coordinates

TIMEOUT = 20
MAX_POM_BYTES = 5 * 1024 * 1024
MAX_MODEL_DEPTH = 60
PROPERTY = re.compile(r"\$\{([^}]+)\}")
RUNTIME_SCOPES = {"compile", "runtime"}


def text(node, path, default=""):
    """Прочитать текст дочернего XML-элемента."""
    return node.findtext(path, default).strip()


def interpolate(value, properties):
    """Подставить свойства; сообщить об отсутствующих и циклических."""
    seen = set()
    while PROPERTY.search(value):
        if value in seen:
            raise ValueError(f"Циклическое свойство POM: {value}")
        seen.add(value)
        def replace(match):
            """Вернуть значение одного свойства."""
            key = match.group(1)
            if key not in properties:
                raise ValueError(f"Неизвестное свойство POM: {key}")
            return properties[key]
        value = PROPERTY.sub(replace, value)
    return value


def dependency_rows(root, path):
    """Прочитать поля зависимостей, сохраняя исходные выражения."""
    fields = ["groupId", "artifactId", "version", "scope", "optional", "type"]
    return [{key: text(node, key) for key in fields}
            for node in root.findall(path)]


def merge_rows(base, extra):
    """Переопределить унаследованные зависимости по имени и типу."""
    result = {}
    for row in base + extra:
        key = (row["groupId"], row["artifactId"], row.get("type") or "jar")
        result[key] = {**result.get(key, {}), **{
            name: value for name, value in row.items() if value
        }}
    return list(result.values())


@dataclass
class PomModel:
    """Свойства, управление версиями и прямые зависимости POM."""

    properties: dict
    managed: list
    dependencies: list


class MavenRepository:
    """Загружать POM и кэшировать модели в пределах одного запуска."""

    def __init__(self, url):
        """Запомнить корневой URL репозитория."""
        self.url = url.rstrip("/")
        self.cache = {}
        self.loading = set()

    def read_xml(self, package):
        """Скачать POM по стандартному пути Maven и разобрать XML."""
        group, artifact, version = coordinates(package)
        path = f"{group.replace('.', '/')}/{artifact}/{version}"
        url = f"{self.url}/{path}/{artifact}-{version}.pom"
        try:
            with urlopen(url, timeout=TIMEOUT) as response:
                data = response.read(MAX_POM_BYTES + 1)
        except HTTPError as error:
            raise ValueError(f"HTTP {error.code}: {url}") from error
        except (URLError, OSError) as error:
            raise ValueError(f"Не удалось скачать {url}: {error}") from error
        if len(data) > MAX_POM_BYTES:
            raise ValueError(f"POM слишком велик: {package}")
        try:
            root = ET.fromstring(data)
        except ET.ParseError as error:
            raise ValueError(f"Некорректный XML POM: {package}") from error
        for node in root.iter():
            node.tag = node.tag.split("}")[-1]
        if root.tag != "project":
            raise ValueError(f"Ожидается элемент project: {package}")
        return root

    def model(self, package):
        """Построить модель с наследованием и защитой от циклов POM."""
        if package in self.cache:
            return self.cache[package]
        if package in self.loading or len(self.loading) >= MAX_MODEL_DEPTH:
            raise ValueError(f"Цикл или слишком глубокое наследование: {package}")
        self.loading.add(package)
        try:
            model = self.build_model(package, self.read_xml(package))
            self.cache[package] = model
            return model
        finally:
            self.loading.remove(package)

    def build_model(self, package, root):
        """Объединить родителя, свойства, BOM и текущие зависимости."""
        group, artifact, version = coordinates(package)
        parent_node = root.find("parent")
        parent = PomModel({}, [], [])
        if parent_node is not None:
            parent_id = ":".join(text(parent_node, key) for key in
                                 ["groupId", "artifactId", "version"])
            parent = self.model(parent_id)
        props = dict(parent.properties)
        for node in root.findall("properties/*"):
            props[node.tag] = (node.text or "").strip()
        for prefix in ["project", "pom"]:
            for key, value in zip(["groupId", "artifactId", "version"],
                                  [group, artifact, version]):
                props[f"{prefix}.{key}"] = value
            if parent_node is not None:
                for key in ["groupId", "artifactId", "version"]:
                    props[f"{prefix}.parent.{key}"] = text(parent_node, key)
        rows = dependency_rows(root, "dependencyManagement/dependencies/dependency")
        managed = self.management(parent.managed, rows, props)
        dependencies = merge_rows(
            parent.dependencies, dependency_rows(root, "dependencies/dependency")
        )
        return PomModel(props, managed, dependencies)

    def management(self, inherited, rows, props):
        """Добавить управляемые версии и импортированные BOM."""
        imports, local = [], []
        for row in rows:
            resolved = {key: interpolate(value, props)
                        for key, value in row.items()}
            if resolved["type"] == "pom" and resolved["scope"] == "import":
                package = ":".join(resolved[key] for key in
                                   ["groupId", "artifactId", "version"])
                bom = self.model(package)
                imports = merge_rows([
                    {key: interpolate(value, bom.properties)
                     for key, value in entry.items()}
                    for entry in bom.managed
                ], imports)
            else:
                local.append(row)
        return merge_rows(merge_rows(inherited, imports), local)

    def direct(self, package, include_all=False):
        """Вернуть координаты прямых зависимостей в порядке POM."""
        model = self.model(package)
        managed = {}
        for row in model.managed:
            item = {key: interpolate(value, model.properties)
                    for key, value in row.items()}
            managed[(item["groupId"], item["artifactId"])] = item
        result = []
        for row in model.dependencies:
            item = {key: interpolate(value, model.properties)
                    for key, value in row.items()}
            defaults = managed.get((item["groupId"], item["artifactId"]), {})
            item = {**defaults, **{k: v for k, v in item.items() if v}}
            scope = item.get("scope", "compile")
            if not include_all and (scope not in RUNTIME_SCOPES or
                                    item.get("optional") == "true"):
                continue
            dependency = ":".join(item.get(key, "") for key in
                                  ["groupId", "artifactId", "version"])
            coordinates(dependency)
            if dependency not in result:
                result.append(dependency)
        return result
