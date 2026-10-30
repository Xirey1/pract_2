# Практическая работа 2. Вариант 11

Инструмент визуализации зависимостей Java (Maven).
Язык: Python 3.10+, только стандартная библиотека.

## Этап 1

Параметры задаются опциями CLI. Имя пакета имеет формат
`groupId:artifactId:version`. В тестовом режиме используются имена A-Z
и путь к JSON-файлу. Булевы опции не принимают значений.

```powershell
.\run.bat --package org.example:demo:1.0 --repository https://repo.maven.apache.org/maven2 --mode config
.\run.bat test
```

`--package` и `--repository` обязательны. `--test-repository` включает
тестовый режим, `--ascii` включает ASCII-дерево на этапе визуализации.
`--mode config` выводит все настройки в формате ключ=значение.
Ошибки параметров завершают программу с кодом 2.

Запуск без скрипта: `python -X utf8 src/main.py` с теми же опциями.
Linux/macOS: `sh run.sh` с теми же опциями; тесты: `sh run.sh test`.
Сборка и установка библиотек не требуются.

## Этап 2

`--mode direct` (по умолчанию на этом этапе) выводит все прямые
зависимости POM, в том числе test/provided/optional. Скачивание выполняет
`urllib.request`, разбор XML - `xml.etree.ElementTree`.
Поддерживаются XML namespace, свойства, родительские POM,
`dependencyManagement`, импорт BOM и кэш моделей в памяти.
Сетевые ошибки, HTTP 404, неверный XML и неизвестные свойства дают код 1.

```powershell
.\run.bat --package junit:junit:4.13.2 --repository https://repo.maven.apache.org/maven2 --mode direct
```
