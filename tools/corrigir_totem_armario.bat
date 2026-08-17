@echo off
title ELEVA LOCKER - Corrigir Totem Armario
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
echo  CORRIGIR TOTEM — armario Matriz + TOTEM_ARMARIO_ID no .env
echo  ==========================================================
echo.

%PYTHON% tools\corrigir_totem_armario.py %*

echo.
pause
