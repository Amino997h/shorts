@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
title AI Shorts Creator - License ^& Launch (v4)

rem Auto-navigate to script directory
cd /d "%~dp0"

echo ========================================================
echo       AI Shorts Creator - Startup ^& Verification (v4)
echo ========================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH!
    pause
    exit /b 1
)

python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python 3.12 64-bit is strictly required!
    echo Current installed Python version:
    python --version
    echo Please install Python 3.12 64-bit from https://www.python.org/
    echo.
    pause
    exit /b 1
)

rem Check for compiled entrypoint first, fallback to .py
set ENTRY_SCRIPT=
if exist web_gui.pyc set ENTRY_SCRIPT=web_gui.pyc
if not defined ENTRY_SCRIPT if exist web_gui.py set ENTRY_SCRIPT=web_gui.py

if not defined ENTRY_SCRIPT (
    echo [ERROR] Neither web_gui.pyc nor web_gui.py was found in this folder!
    echo Please make sure you extracted all files from the ZIP before running.
    echo.
    pause
    exit /b 1
)

rem Check for compiled auth entrypoint first, fallback to .py
set AUTH_SCRIPT=
if exist auth_guard.pyc set AUTH_SCRIPT=auth_guard.pyc
if not defined AUTH_SCRIPT if exist auth_guard.py set AUTH_SCRIPT=auth_guard.py

echo Checking License Status...
python %AUTH_SCRIPT%
if errorlevel 1 (
    echo.
    echo [ERROR] License validation failed or cancelled.
    pause
    exit /b 1
)

echo.
echo Launching web interface...
python %ENTRY_SCRIPT%
if errorlevel 1 (
    echo.
    echo [ERROR] The application stopped unexpectedly.
    pause
)
