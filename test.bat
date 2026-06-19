@echo off
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo  Initializing Local Laboratory Hardware Interface  
echo ====================================================
set "CONDA_PATH=%USERPROFILE%\Miniconda3"
set "CONDA_EXE=%CONDA_PATH%\Scripts\conda.exe"
set "CONDA_BAT=%CONDA_PATH%\condabin\conda.bat"

REM set CMD="powershell -Command "[target.Process]::Start('cmd.exe', '/k call %CONDA_BAT% activate behavior-chamber-host && python host_serial_proxy.py').Id" > proxy.pid"
REM echo %CMD%

REM start "BehaviorChamberProxy" cmd /k "call "%CONDA_BAT%" activate behavior-chamber-host && python host_serial_proxy.py"
REM start "BehaviorChamberProxy" cmd /k "call "%CONDA_BAT%" activate behavior-chamber-host && python host_serial_proxy.py BehaviorChamberProxyFlag"

set "terinalTitle=BehaviorChamberProxy"
set "commandToRun=call "%CONDA_BAT%" activate behavior-chamber-host && python host_serial_proxy.py"


:: Start the window and capture its PID
for /f %%A in ('powershell -Command "(Start-Process cmd -ArgumentList '/k %commandToRun%' -WindowStyle Normal -PassThru).Id"') do set "PROXY_PID=%%A"

:: Set the window title using the captured PID if desired
title %terminalTitle%
timeout /t 1 >nul
echo Started terminal with PID: %PROXY_PID%

tasklist /V /FI "IMAGENAME eq cmd.exe"

pause
REM for /f "tokens=2" %%a in ('tasklist /nh /fi "imagename eq notepad.exe"') do (
REM     set "PID=%%a"
REM )

REM for /f "tokens=2 delims=," %%A in ('tasklist /V /FO CSV /NH ^| findstr /I "BehaviorChamberProxy"') do (
REM    set "PID=%%A"
REM )
REM echo PID: %PID%
REM taskkill /PID %%~A /T /F
REM taskkill /FI "WINDOWTITLE eq BehaviorChamberProxy" /T /F

if defined PROXY_PID (
    taskkill /PID %PROXY_PID% /T /F 
)

REM taskkill /FI "WINDOWTITLE eq BehaviorChamberProxy" /T /F

pause