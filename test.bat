@echo off
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo  Initializing Local Laboratory Hardware Interface  
echo ====================================================
set "CONDA_PATH=%USERPROFILE%\Miniconda3"
set "CONDA_EXE=%CONDA_PATH%\Scripts\conda.exe"
set "CONDA_BAT=%CONDA_PATH%\condabin\conda.bat"
set CMD="title BehaviorChamberProxy
set CMD=%CMD% && call %CONDA_BAT% activate behavior-chamber-host
set CMD=%CMD% && python host_serial_proxy.py"
echo %CMD%
start cmd /k %CMD%

pause

taskkill /FI "WINDOWTITLE eq BehaviorChamberProxy" /T /F >nul 2>&1