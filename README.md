# Практическая работа №2

Вариант 11. Программа строит граф зависимостей пакетов Maven
и выводит его в Mermaid или в виде ASCII-дерева.
Написана на Python 3.10+, дополнительные библиотеки не нужны.

## Запуск

Команды выполняются из папки проекта. Пример с локальным графом:

```powershell
.\run.bat --package A --repository examples/diamond.json --test-repository --ascii
```

Пример с пакетом Maven:

```powershell
.\run.bat --package junit:junit:4.13.2 --repository https://repo.maven.apache.org/maven2 --ascii
```

Можно запускать напрямую: `python -X utf8 src/main.py` с теми же аргументами.
На Linux: `sh run.sh` с теми же аргументами.

## Параметры

| Параметр | Для чего нужен |
| --- | --- |
| `--package` | Пакет в формате groupId:artifactId:version; в тестовом режиме, например, A |
| `--repository` | URL репозитория Maven или путь к JSON с тестовым графом |
| `--test-repository` | Работа с локальным JSON вместо Maven |
| `--ascii` | Дополнительный вывод ASCII-дерева |
| `--mode` | Режим: config, direct, graph или order; по умолчанию graph |
| `--help` | Справка по запуску |

`--package` и `--repository` обязательны. Флаги `--ascii` и
`--test-repository` указываются без значений.

Режимы: `config` выводит настройки, `direct` - прямые зависимости,
`graph` - граф Mermaid, `order` - порядок загрузки зависимостей.
Флаг `--ascii` используется с graph; в config выводится его значение.

Например, порядок загрузки для тестового графа:

```powershell
.\run.bat --package A --repository examples/diamond.json --test-repository --mode order
```

## Как устроена программа

Граф строится обходом в ширину (BFS) с рекурсивным переходом между уровнями.
Уже найденные вершины запоминаются, поэтому циклы не вызывают бесконечный обход.
Порядок загрузки определяется алгоритмом Кана: зависимости идут раньше
пакетов, которым они нужны. Для графа с циклом порядок построить нельзя.

| Файл | Функции и классы |
| --- | --- |
| `src/main.py` | `main` выбирает режим и выводит результат |
| `src/config.py` | `parse_args`, `validate`, `coordinates` проверяют параметры; `format_config` выводит настройки |
| `src/maven.py` | `text`, `dependency_rows` читают XML; `interpolate` подставляет свойства; `merge_rows` объединяет зависимости |
| `src/maven.py` | `PomModel` хранит данные; `MavenRepository` загружает POM и хранит кэш |
| `src/maven.py` | `read_xml` скачивает POM; `model`, `build_model` собирают модель; `management` читает BOM; `direct` возвращает зависимости |
| `src/graph.py` | `TestRepository` читает и проверяет JSON (`validate_node`, `direct`); `build_graph`, `visit_level` выполняют BFS |
| `src/operations.py` | `loading_order` вычисляет порядок загрузки |
| `src/render.py` | `mermaid` формирует диаграмму; `ascii_tree`, `push_children` формируют дерево |

Тестовые графы находятся в `examples/`: цепочка, ромб, цикл, петля
и отдельная вершина. Формат JSON: `"A": ["B", "C"]` означает,
что A зависит от B и C. Все вершины нужно объявить, листья записываются как `[]`.
В ASCII-дереве `[cycle]` обозначает цикл, `[shared]` - общую зависимость,
которая уже показана в другой ветке.

## Проверка

```powershell
.\run.bat test
```

Тесты написаны на unittest. Без скрипта:
`python -X utf8 -m unittest discover -s tests -v`.
На Linux: `sh run.sh test`. Сборка проекта не требуется.

В `scripts/` находятся отдельные проверки:
`real_examples.py` получает три примера и собирает страницу диаграмм
(`main`, `write_gallery`), `compare_maven.py` запускает Maven (`main`, `run`),
`verify_comparison.py` сравнивает сохраненные ребра
(`main`, `maven_edges`, `mermaid_edges`).

[Примеры диаграмм](docs/EXAMPLES.md) · [Сравнение с Maven](docs/COMPARISON.md)

## Ограничения

В граф входят compile/runtime-зависимости без optional. Режим direct
выводит все прямые зависимости, включая test/provided/optional.
Поддерживаются свойства, родительские POM, dependencyManagement и BOM.
Профили, exclusions, выбор одной версии при конфликте, classifiers,
диапазоны версий, SNAPSHOT, relocation и дополнительные репозитории из POM
не реализованы. Разные версии одного пакета считаются разными вершинами.

При неверных аргументах программа возвращает код 2, при ошибке данных
или сети - 1, при успешном выполнении - 0.
