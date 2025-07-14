@echo off
setlocal

REM Get script location
set BASEDIR=%~dp0
echo Starting Angular frontend...
start cmd /k "cd /d %BASEDIR%Angular Files && ng serve --o"

echo Starting Flask backend...
start cmd /k "cd /d %BASEDIR%Flask Project Files\pythonBackend && call .venv\Scripts\activate && set FLASK_APP=application.py && set FLASK_ENV=development && flask run"
