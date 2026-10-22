@echo off
title Creating Client Protected Package (v4)...
echo ========================================================
echo       Generating Protected Client Package (v4)
echo ========================================================
echo.

set RELEASE_DIR=AI_Shorts_Client_Release

echo 1. Cleaning old release folder...
if exist "%RELEASE_DIR%" rd /s /q "%RELEASE_DIR%"
if exist dist rd /s /q dist

echo 2. Obfuscating core security module (auth_guard.py)...
pyarmor gen auth_guard.py

if errorlevel 1 (
    echo [ERROR] PyArmor obfuscation failed!
    pause
    exit /b
)

echo.
echo 3. Creating client release folder: %RELEASE_DIR%...
mkdir "%RELEASE_DIR%"

echo 4. Copying protected auth_guard and pyarmor security runtime...
xcopy /E /I /Y dist\* "%RELEASE_DIR%\" >nul

echo 5. Copying application scripts and assets...
copy /Y web_gui.py "%RELEASE_DIR%\" >nul
copy /Y video_maker.py "%RELEASE_DIR%\" >nul
copy /Y install.bat "%RELEASE_DIR%\" >nul
copy /Y start.bat "%RELEASE_DIR%\" >nul
copy /Y config.json "%RELEASE_DIR%\" >nul

echo.
echo ========================================================
echo   SUCCESS! The client package is ready in:
echo   %RELEASE_DIR%
echo ========================================================
echo.
pause
