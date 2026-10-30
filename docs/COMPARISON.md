# Сравнение с Maven

Проверено 30 октября 2026 года на Python 3.12.
Для сравнения использовались Maven 3.9.9, Java 1.8.0_503
и maven-dependency-plugin 3.6.1.

## Как воспроизвести

```powershell
.\run.bat test
python -X utf8 scripts/real_examples.py
python -X utf8 scripts/compare_maven.py --maven mvn
python -X utf8 scripts/verify_comparison.py
```

Для сравнения используется `examples/maven-comparison/pom.xml`.
В нем одна зависимость, выбираемая свойствами sample.group,
sample.artifact и sample.version. Скрипт запускает для каждого пакета
`org.apache.maven.plugins:maven-dependency-plugin:3.6.1:tree`
с `-Dscope=runtime`, затем goal `resolve` с `-DincludeScope=runtime`.
Это сопоставляет compile/runtime-графы, без тестовых зависимостей.

Кэш Maven хранится в `tools/m2`, он не добавляется в Git.
Maven нужен для сравнения. Само приложение читает POM через urllib
и разбирает XML стандартной библиотекой Python.

## Сравнение графов

| Пакет | Вершины | Ребра | Совпадение с Maven |
| --- | ---: | ---: | --- |
| junit:junit:4.13.2 | 2 | 1 | Полное |
| org.apache.commons:commons-text:1.12.0 | 2 | 1 | Полное |
| com.fasterxml.jackson.core:jackson-databind:2.17.2 | 3 | 2 | Полное |

Учитывается подграф выбранного пакета. Служебный корень
`student:comparison:1.0` из проекта сравнения исключен.
Проверка `scripts/verify_comparison.py` восстановила ребра из Mermaid
и настоящего вывода Maven и сравнила множества ребер:

```text
junit:junit:4.13.2: MATCH (1 edges)
org.apache.commons:commons-text:1.12.0: MATCH (1 edges)
com.fasterxml.jackson.core:jackson-databind:2.17.2: MATCH (2 edges)
```

Диаграммы Mermaid и ASCII: [EXAMPLES.md](EXAMPLES.md).
Сырые результаты находятся в `examples/` этой папки,
реальные протоколы Maven - в `maven/`. Все шесть команд Maven
завершились кодом 0 и сообщением `BUILD SUCCESS`.
В протоколах опущены абсолютный путь проекта, время завершения
и длительность, остальные сообщения сохранены.

## Сравнение порядка загрузки

Ниже для краткости используются artifactId; полные координаты
и версии находятся в `examples/*.order.txt` и `maven/*.resolve.txt`.

| Пакет | Порядок программы | Порядок списка Maven resolve |
| --- | --- | --- |
| junit | hamcrest-core, junit | junit, hamcrest-core |
| commons-text | commons-lang3, commons-text | commons-text, commons-lang3 |
| jackson-databind | jackson-annotations, jackson-core, jackson-databind | jackson-databind, jackson-annotations, jackson-core |

Программа строит топологический порядок: каждый пакет располагается
после всех своих зависимостей. Maven `resolve` показывает список
разрешенных артефактов; этот список не является топологической сортировкой
и в общем случае не отражает хронологию сетевых запросов.

Для Commons Text в сохраненном протоколе также есть фактические сообщения
`Downloading`/`Downloaded`: сначала скачан commons-text:1.12.0,
затем commons-lang3:3.14.0. Это обратный порядок относительно результата
программы. Скачивание JAR не требует, чтобы JAR его зависимостей уже
находились на диске, поэтому Maven может использовать такую очередность.
Для JUnit и Jackson JAR находились в кэше: их фактическая хронология
сетевой загрузки в этих протоколах не измерялась.

Тестовые графы демонстрируют свойства алгоритма независимо от сети:

| Пример | Порядок |
| --- | --- |
| chain.json | C, B, A |
| diamond.json | D, B, C, A |
| isolated.json | A |
| cycle.json | Ошибка: корректный порядок невозможен |
| self_cycle.json | Ошибка: корректный порядок невозможен |

## Тесты

`run.bat test`: 27 тестов, результат `OK`.
Проверяются параметры запуска, разбор POM, свойства, родители, BOM,
ошибки сети и XML, обход графа, циклы, порядок загрузки и вывод диаграмм.

## Возможные расхождения на других пакетах

Реализация не активирует Maven profiles, не применяет exclusions,
не разрешает конфликты по nearest-wins и не передает dependencyManagement
корня на весь граф. Также не поддерживаются classifiers, диапазоны
версий, SNAPSHOT metadata, relocation и дополнительные репозитории POM.
Разные версии артефакта сохраняются как разные вершины. При использовании
этих механизмов результат может отличаться от эффективного графа Maven.
Список ограничений также приведен в [README](../README.md#ограничения).

Официальные источники для правил Maven:

- [Механизм зависимостей](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html).
- [Описание POM](https://maven.apache.org/pom.html).
- [dependency:tree](https://maven.apache.org/plugins/maven-dependency-plugin/tree-mojo.html).
- [dependency:resolve](https://maven.apache.org/plugins/maven-dependency-plugin/resolve-mojo.html).
