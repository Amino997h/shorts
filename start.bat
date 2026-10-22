@echo off
title AI Shorts Creator - License & Launch (v4)
echo ========================================================
echo       AI Shorts Creator - Startup & Verification (v4)
echo ========================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH!
    pause
    exit /b
)

echo Checking License Status...
python -c "import auth_guard; auth_guard.check_access_or_prompt()"

if errorlevel 1 (
    echo.
    echo [ERROR] License validation failed or cancelled.
    pause
    exit /b
)

echo.
echo Launching web interface...
start http://127.0.0.1:7860
python web_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] The application stopped unexpectedly.
    pause
)
