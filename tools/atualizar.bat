@echo off
title ELEVA LOCKER - Atualizar automatico
color 0A
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"

if not defined PYTHON (
    echo ERRO: Python nao encontrado no PATH.
    pause
    exit /b 1
)

echo.
echo  ELEVA LOCKER — Atualizacao automatica (git + reinicio)
echo  Branch: cursor/totem-seguro-c05c
echo  ========================================================
echo.

if "%~1"=="" (
    %PYTHON% tools\atualizar.py --branch cursor/totem-seguro-c05c
) else (
    %PYTHON% tools\atualizar.py %*
)

echo.
pause
