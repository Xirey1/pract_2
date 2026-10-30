@echo off
setlocal
cd /d "%~dp0"
if defined PYTHON goto run
set "PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%PYTHON%" goto run
set "PYTHON=python"
:run
if "%~1"=="test" goto test
"%PYTHON%" -X utf8 src\main.py %*
exit /b %errorlevel%
:test
"%PYTHON%" -X utf8 -m unittest discover -s tests -v
exit /b %errorlevel%
