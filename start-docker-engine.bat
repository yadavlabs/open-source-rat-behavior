@echo off

SETLOCAL EnableDelayedExpansion
echo Checking docker status...

REM Check if Docker is running by executing 'docker info'
docker info >nul 2>&1

if %errorlevel% neq 0 (
    echo Docker is NOT running. Starting Docker Desktop...
    echo %USERPROFILE%
    set "DOCKER_PATH=%USERPROFILE%\AppData\Local\Programs\DockerDesktop"
    REM echo DOCKER_PATH: !DOCKER_PATH!\Docker Desktop.exe
    if not exist "!DOCKER_PATH!\Docker Desktop.exe" (
        set "DOCKER_PATH=C:\Program Files\Docker\Docker"
    )
    REM echo DOCKER_PATH: !DOCKER_PATH!\Docker Desktop.exe
    :: Launch Docker Desktop using its default installation path
    start /MIN "" "!DOCKER_PATH!\Docker Desktop.exe" --nosplash
    
    echo Waiting for Docker to fully initialize...
    :wait_loop
    REM timeout /t 3 /nobreak >nul
    REM avoid using timeout for better compatibility, use ping to wait
    ping 127.0.0.1 -n 4 >nul
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        goto wait_loop
    )
    echo Docker has started successfully!
) else (
    echo Docker is already running.
)

exit /b 0
