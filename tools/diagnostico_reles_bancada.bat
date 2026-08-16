@echo off
setlocal EnableDelayedExpansion
title ELEVA LOCKER - Diagnostico reles Bancada
color 0E
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
echo   DIAGNOSTICO RELES — Bancada portas 9-24
echo ============================================================
echo.

"%PYTHON%" tools\diagnostico_reles_bancada.py %*

if errorlevel 1 (
    echo.
    set /p FIX="Corrigir mapeamento agora? (S/N): "
    if /i "!FIX!"=="S" (
        "%PYTHON%" tools\diagnostico_reles_bancada.py --corrigir
        "%PYTHON%" tools\diagnostico_reles_bancada.py
    )
)

echo.
pause
