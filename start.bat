@echo off
title AI Shorts Creator - Web Dashboard
echo ========================================================
echo       Starting AI Shorts Creator Dashboard (v3)...
echo ========================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH!
    pause
    exit /b
)

echo Launching web interface...
start http://127.0.0.1:7860
python web_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] The application stopped unexpectedly.
    pause
)
