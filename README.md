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
