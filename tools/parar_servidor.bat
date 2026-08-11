@echo off
title ELEVA LOCKER - Parar servidor
color 0C
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

%PYTHON% tools\parar_servidor.py
if "%~1"=="" (
echo.
pause
)
