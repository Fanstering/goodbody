@echo off
title Create Desktop Shortcut
cd /d "%~dp0"

echo Creating shortcut...

:: Use PowerShell to create shortcut with dynamic paths
powershell -NoProfile -Command "$WshShell = New-Object -ComObject WScript.Shell; $s = $WshShell.CreateShortcut('%~dp0健身打卡.lnk'); $s.TargetPath = 'python.exe'; $s.Arguments = '\"%~dp0app.py\"'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'Fitness Tracker - double click to start'; $s.WindowStyle = 1; $s.Save()"

if exist "%~dp0健身打卡.lnk" (
    echo.
    echo ========================================
    echo   Shortcut created successfully!
    echo   File: 健身打卡.lnk
    echo ========================================
    echo.
    echo Double-click 健身打卡.lnk to start the app.
    echo Note: Make sure Python is in your system PATH.
) else (
    echo.
    echo [ERROR] Failed to create shortcut.
    echo Please try running this script as administrator.
)
echo.
pause
