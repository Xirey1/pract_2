"""Проверки самостоятельного разбора Maven POM."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from maven import MavenRepository, interpolate


def pom(body):
    """Создать минимальный POM без XML namespace."""
    return ET.fromstring(f"<project>{body}</project>")


def dependency(artifact, version="1", extra=""):
    """Создать описание зависимости для теста."""
    return (f"<dependency><groupId>g</groupId>"
            f"<artifactId>{artifact}</artifactId>"
            f"<version>{version}</version>{extra}</dependency>")


class MavenTests(unittest.TestCase):
    """Наследование, свойства, BOM, фильтрация и ошибки сети."""

    def test_parent_properties_management(self):
        """Наследовать версию и переопределить свойство в потомке."""
        parent = pom("<properties><v>2</v></properties>"
                     "<dependencyManagement><dependencies>"
                     + dependency("b", "${v}")
                     + "</dependencies></dependencyManagement>")
        child = pom("<parent><groupId>g</groupId>"
                    "<artifactId>parent</artifactId><version>1</version>"
                    "</parent><properties><v>3</v></properties>"
                    "<dependencies>" + dependency("b", "")
                    + "</dependencies>")
        repo = MavenRepository("https://repo.test")
        with patch.object(repo, "read_xml", side_effect=[child, parent]):
            self.assertEqual(repo.direct("g:a:1"), ["g:b:3"])
            self.assertEqual(repo.direct("g:a:1"), ["g:b:3"])

    def test_scopes_and_optional(self):
        """Все прямые зависимости и фильтр графа различаются."""
        root = pom("<dependencies>" + dependency("a")
                   + dependency("b", extra="<scope>test</scope>")
                   + dependency("c", extra="<optional>true</optional>")
                   + dependency("d", extra="<scope>runtime</scope>")
                   + "</dependencies>")
        repo = MavenRepository("https://repo.test")
        with patch.object(repo, "read_xml", return_value=root):
            self.assertEqual(repo.direct("g:root:1"), ["g:a:1", "g:d:1"])
            self.assertEqual(len(repo.direct("g:root:1", True)), 4)

    def test_bom(self):
        """Импортировать управляемые версии из BOM."""
        root = pom("<dependencyManagement><dependencies>"
                   + dependency("bom", extra="<type>pom</type>"
                                "<scope>import</scope>")
                   + "</dependencies></dependencyManagement>"
                   "<dependencies>" + dependency("b", "")
                   + "</dependencies>")
        bom = pom("<dependencyManagement><dependencies>"
                  + dependency("b", "4")
                  + "</dependencies></dependencyManagement>")
        repo = MavenRepository("https://repo.test")
        with patch.object(repo, "read_xml", side_effect=[root, bom]):
            self.assertEqual(repo.direct("g:a:1"), ["g:b:4"])

    def test_property_errors(self):
        """Не скрывать циклы и неизвестные свойства."""
        for props in [{}, {"v": "${v}"}, {"v": "${w}", "w": "${v}"}]:
            with self.subTest(props=props), self.assertRaises(ValueError):
                interpolate("${v}", props)

    def test_parent_cycle(self):
        """Остановить циклическое наследование."""
        root = pom("<parent><groupId>g</groupId><artifactId>a</artifactId>"
                   "<version>1</version></parent>")
        repo = MavenRepository("https://repo.test")
        with patch.object(repo, "read_xml", return_value=root):
            with self.assertRaisesRegex(ValueError, "Цикл"):
                repo.direct("g:a:1")

    def test_http_and_network_errors(self):
        """Показать понятную ошибку вместо traceback."""
        errors = [HTTPError("url", 404, "missing", {}, None), URLError("DNS")]
        for error in errors:
            with patch("maven.urlopen", side_effect=error):
                with self.assertRaises(ValueError):
                    MavenRepository("https://repo.test").direct("g:a:1")
