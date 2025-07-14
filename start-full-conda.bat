@echo off
setlocal

REM Get script location
set BASEDIR=%~dp0
echo Starting Angular frontend...
start cmd /k "cd /d %BASEDIR%Angular Files && ng serve --o"

echo Starting Flask backend...

REM Set to name of conda environment
set ENV_NAME=behavior-chamber-env

REM May need to change depending on how anaconda was installed
set ENV_PATH=%USERPROFILE%\anaconda3\condabin\

call %ENV_PATH%activate.bat
set CMD="cd /d %BASEDIR%Flask Project Files\pythonBackend 
set CMD=%CMD% && echo Activating conda environment %ENV_NAME%...
set CMD=%CMD% && call conda activate %ENV_NAME%
set CMD=%CMD% && echo Starting backend...
set CMD=%CMD% && set FLASK_APP=application.py 
set CMD=%CMD% && set FLASK_DEBUG=true
set CMD=%CMD% && flask run"

start cmd /k %CMD%