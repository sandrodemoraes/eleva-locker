@echo off
title ELEVA LOCKER - Backup Obrigatorio
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
echo  BACKUP OBRIGATORIO — banco + .env (+ D: se existir)
echo  ===================================================
echo.

%PYTHON% tools\backup_obrigatorio.py %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" (
    echo  ATUALIZACAO BLOQUEADA — corrija o backup antes de continuar.
)
pause
exit /b %RC%
