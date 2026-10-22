@echo off
title Creating Client Protected Package (v4)...
echo ========================================================
echo       Generating Protected Client Package (v4)
echo ========================================================
echo.

python build_release_v4.py
if errorlevel 1 (
    echo.
    echo [ERROR] Build release failed!
    pause
    exit /b
)

echo.
echo Creating final ZIP package (No plain python code!)...
powershell -Command "Compress-Archive -Path 'AI_Shorts_Client_Release\*' -DestinationPath 'AI_Shorts_Pro.zip' -Force"

echo.
echo ========================================================
echo   SUCCESS! 100%% Protected AI_Shorts_Pro.zip is ready!
echo   All .py sources are removed/encrypted!
echo ========================================================
echo.
pause
