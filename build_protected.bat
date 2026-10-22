@echo off
title Obfuscating AI Shorts Creator (v4)...
echo ========================================================
echo       Building Protected Release with PyArmor (v4)
echo ========================================================
echo.

echo 1. Cleaning previous dist folder...
if exist dist rd /s /q dist

echo 2. Obfuscating core license module...
pyarmor gen auth_guard.py

echo.
echo 3. Copying protected runtime to root...
if exist dist\pyarmor_runtime_000000 (
    xcopy /E /I /Y dist\pyarmor_runtime_000000 pyarmor_runtime_000000 >nul
    copy /Y dist\auth_guard.py auth_guard.py >nul
    echo [OK] Core authorization module is now fully encrypted!
) else (
    echo [ERROR] Obfuscation failed!
    pause
    exit /b
)

echo.
echo ========================================================
echo   Protection Completed! auth_guard.py is now encrypted.
echo ========================================================
echo.
pause
