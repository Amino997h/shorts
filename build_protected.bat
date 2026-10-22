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

echo 2. Obfuscating core interfaces (auth_guard.py + web_gui.py)...
pyarmor gen auth_guard.py web_gui.py

if errorlevel 1 (
    echo [ERROR] PyArmor obfuscation failed!
    pause
    exit /b
)

echo.
echo 3. Creating client release folder: %RELEASE_DIR%...
mkdir "%RELEASE_DIR%"

echo 4. Copying obfuscated scripts (auth_guard.py + web_gui.py) and runtime...
xcopy /E /I /Y dist\* "%RELEASE_DIR%\" >nul

echo 5. Copying video engine and launchers...
copy /Y video_maker.py "%RELEASE_DIR%\" >nul
copy /Y install.bat "%RELEASE_DIR%\" >nul
copy /Y start.bat "%RELEASE_DIR%\" >nul
copy /Y config.json "%RELEASE_DIR%\" >nul

echo 6. Creating final ZIP package...
powershell -Command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath 'AI_Shorts_Pro.zip' -Force"

echo.
echo ========================================================
echo   SUCCESS! Protected AI_Shorts_Pro.zip has been updated!
echo ========================================================
echo.
pause
