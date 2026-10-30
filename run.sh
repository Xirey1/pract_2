#!/bin/sh
cd "$(dirname "$0")" || exit 1
if [ "$1" = "test" ]; then
    exec "${PYTHON:-python3}" -X utf8 -m unittest discover -s tests -v
fi
exec "${PYTHON:-python3}" -X utf8 src/main.py "$@"
