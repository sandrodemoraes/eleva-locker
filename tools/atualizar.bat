@echo off
title ELEVA LOCKER - Atualizar (Matriz)
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
echo  ELEVA LOCKER — Atualizar Matriz (backup + git + setup + reinicio)
echo  Backup OBRIGATORIO antes de qualquer alteracao — aborta se falhar
echo  ==================================================================
echo.

%PYTHON% tools\atualizar_matriz.py %*

echo.
pause
