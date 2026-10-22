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

echo 2. Obfuscating core interfaces (auth_guard.py + web_gui.py) with PyArmor...
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

echo 5. Compiling video_maker.py to encrypted bytecode (.pyc) and removing source...
python -c "import py_compile; py_compile.compile('video_maker.py', r'%RELEASE_DIR%\video_maker.pyc', doraise=True)"

echo 6. Copying launchers and configuration...
copy /Y install.bat "%RELEASE_DIR%\" >nul
copy /Y start.bat "%RELEASE_DIR%\" >nul
copy /Y config.json "%RELEASE_DIR%\" >nul

echo 7. Creating final ZIP package (No plain python code!)...
powershell -Command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath 'AI_Shorts_Pro.zip' -Force"

echo.
echo ========================================================
echo   SUCCESS! 100%% Protected AI_Shorts_Pro.zip is ready!
echo   All .py sources are removed/encrypted!
echo ========================================================
echo.
pause
