@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
title Installing AI Shorts Creator Dependencies...
echo ========================================================
echo       AI Shorts Creator - Automatic Setup (v4)
echo ========================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python 3.12 64-bit from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python 3.12 64-bit is required for compiled bytecode!
    echo Current version:
    python --version
    echo Please install Python 3.12 from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Installing required Python packages...
pip install moviepy==1.0.3 faster-whisper edge-tts requests gradio pillow gtts pydub kokoro-onnx soundfile pyttsx3 json-repair

if errorlevel 1 (
    echo.
    echo [ERROR] Package installation failed. Please check your internet connection.
    pause
    exit /b 1
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
