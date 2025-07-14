@echo off
setlocal

REM Get script location
set BASEDIR=%~dp0
echo Starting Angular frontend...
start cmd /k "cd /d %BASEDIR%Angular Files && ng serve --o"

echo Starting Flask backend...
REM Set to name of virtual environment
set ENV_NAME=.venv

REM Set to directory of virtual environment
set ENV_DIR=%BASEDIR%Flask Project Files\pythonBackend

set CMD="cd /d %ENV_DIR% && echo Activating virtual environment %ENV_NAME%...
set CMD=%CMD% && call %ENV_NAME%\Scripts\activate
set CMD=%CMD% && echo Starting backend...
set CMD=%CMD% && set FLASK_APP=application.py
REM set CMD=%CMD% && set FLASK_ENV=development
set CMD=%CMD% && set FLASK_DEBUG=true
set CMD=%CMD% && flask run"

REM set CMD=%CMD% "&& flask run"

start cmd /k %CMD%
