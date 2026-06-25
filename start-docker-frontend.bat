@echo off
if "%~1"=="-FIXED_CTRL_C" (
    shift
) else (
    call <NUL %0 -FIXED_CTRL_C %*
    goto :EOF
)
SETLOCAL EnableDelayedExpansion

REM 2 Launch the Docker container
echo ----------------------------------------------------
echo  Booting Docker Web Containers (Angular + Flask)
echo  Press Ctrl+C in this window to stop the servers.
echo ----------------------------------------------------
REM cmd /c "docker compose down && docker compose up"
call docker compose down frontend
call docker compose up frontend
