@echo off
if "%~1"=="-FIXED_CTRL_C" (
    shift
) else (
    call <NUL %0 -FIXED_CTRL_C %*
    goto :EOF
)
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo  Starting Docker Engine and Local Laboratory Hardware Interface
echo ====================================================
call "%~dp0start-docker-engine.bat"
if errorlevel 1 (
    echo [ERROR] Failed to start Docker Engine.
    pause
    exit /b
)
echo ====================================================
echo  Initializing Local Laboratory Hardware Interface  
echo ====================================================

REM 1. Setup hardware environment
REM 1.1 Locate Miniconda installation
set "CONDA_PATH=%USERPROFILE%\Miniconda3"
if not exist "%CONDA_PATH%\Scripts\conda.exe" (
    set "CONDA_PATH=%USERPROFILE%\AppData\Local\Miniconda3"
)
if not exist "%CONDA_PATH%\Scripts\conda.exe" (
    set "CONDA_PATH=%ProgramData%\Miniconda3"
)

REM exit if no conda installation is found (could also check for Anaconda)
if not exist "%CONDA_PATH%\Scripts\conda.exe" (
    echo [ERROR] No conda installation found. Please install Miniconda or Anaconda.
    pause
    exit /b
)

REM 1.2 Setup the conda environment
set "CONDA_EXE=%CONDA_PATH%\Scripts\conda.exe"
set "CONDA_BAT=%CONDA_PATH%\condabin\conda.bat"
echo [1/3] Checking for host hardware environment...
call "%CONDA_BAT%" env list | findstr "behavior-chamber-host" >nul
if errorlevel 1 (
    echo [1/3] Environment not found. Creating conda environment 'behavior-chamber-host'...
    call "%CONDA_EXE%" create -y -n behavior-chamber-host python=3.8
)

REM 1.3 activate and check dependencies
echo [2/3] Syncing host serial driver extensions...
call "%CONDA_BAT%" activate behavior-chamber-host
call conda install -y --file requirements-host.txt || call pip install --quiet -r requirements-host.txt

REM 1.4 Start the host hardware interface
echo [3/3] Spawning Hardware Proxy Server...
:: 'start' runs the proxy inside its own conda-activated command prompt window
set "terinalTitle=SerialPortProxy"
pause
set "commandToRun=call "%CONDA_BAT%" activate behavior-chamber-host && python host_serial_proxy.py"
if errorlevel 1 (
    echo [3/3] Failed to start Hardware Proxy Server.
    pause
    exit /b
)

REM start "SerialPortProxy" cmd /k "call %CONDA_BAT% activate behavior-chamber-host && python host_serial_proxy.py"
for /f %%A in ('powershell -Command "(Start-Process cmd -ArgumentList '/k %commandToRun%' -WindowStyle Normal -PassThru).Id"') do set "PROXY_PID=%%A"
title %terminalTitle%

echo Started terminal with PID: %PROXY_PID%

REM 2 Launch the Docker container
echo ----------------------------------------------------
echo  Booting Docker Web Containers (Angular + Flask)
echo  Press Ctrl+C in this window to stop the servers.
echo ----------------------------------------------------
REM cmd /c "docker compose down && docker compose up"
call docker compose down
call docker compose up
REM start /wait cmd /c "docker compose down && docker compose up"



echo ----------------------------------------------------
echo  Stopping background hardware servers...
echo ----------------------------------------------------
REM taskkill /FI "WINDOWTITLE eq SerialPortProxy*" /T /F >nul 2>&1
if defined PROXY_PID (
    taskkill /PID %PROXY_PID% /T /F 
)
echo  All local server systems offline.
echo ----------------------------------------------------
pause

