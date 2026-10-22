@echo off
title Installing AI Shorts Creator Dependencies...
echo ========================================================
echo       AI Shorts Creator - Automatic Setup (v3)
echo ========================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

echo.
echo Installing required Python packages...
pip install moviepy==1.0.3 faster-whisper edge-tts requests gradio pillow

if errorlevel 1 (
    echo.
    echo [ERROR] Package installation failed. Please check your internet connection.
    pause
    exit /b
)

echo.
echo Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] FFmpeg was NOT detected in your system PATH!
    echo Video rendering requires FFmpeg.
    echo Please install FFmpeg (e.g. winget install Gyan.FFmpeg) or download it from https://ffmpeg.org/
    echo.
) else (
    echo [OK] FFmpeg is installed and ready!
)

echo.
echo ========================================================
echo       Installation Completed Successfully!
echo   You can now launch the app using: start.bat
echo ========================================================
echo.
pause
