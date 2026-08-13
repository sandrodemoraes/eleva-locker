@echo off
title ELEVA LOCKER - Verificar Matriz
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
echo  VERIFICAR MATRIZ — .env + banco + firmware
echo  ==========================================
echo.

%PYTHON% tools\verificar_matriz.py %*

echo.
pause
