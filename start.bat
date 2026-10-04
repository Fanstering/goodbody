@echo off
title Fitness Tracker
cd /d "%~dp0"

echo ========================================
echo       Fitness Tracker App
echo ========================================
echo.

:: Try to find Python
where python >nul 2>nul
if %errorlevel%==0 (
    echo Starting server... browser will open automatically.
    echo Close this window to stop the app.
    echo.
    python app.py
) else (
    echo [ERROR] Python not found in PATH.
    echo.
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    echo and make sure to check "Add Python to PATH" during installation.
    echo.
    echo If you use Anaconda, please activate your environment first:
    echo   conda activate your_env_name
    echo.
    pause
)
