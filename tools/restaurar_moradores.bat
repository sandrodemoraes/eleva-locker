@echo off
title ELEVA LOCKER - Restaurar Moradores Totem
color 0E
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo.
echo  RESTAURAR MORADORES — autocomplete totem deposito
echo  ==================================================
echo.

%PYTHON% tools\restaurar_moradores.py %*
pause
