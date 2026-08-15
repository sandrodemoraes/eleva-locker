@echo off
title ELEVA LOCKER - Restaurar firmware ESP
color 0A
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo ============================================================
echo   RESTAURAR firmware elevalocker_sync.ino (~700 linhas)
echo ============================================================
echo.

"%PYTHON%" tools\restaurar_firmware.py %*

echo.
pause
