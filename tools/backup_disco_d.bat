@echo off
title ELEVA LOCKER - Backup Disco D
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
echo  BACKUP DISCO D: — rotativo + espelho projeto
echo  =============================================
echo.

%PYTHON% tools\backup_disco_d.py %*
set "RC=%ERRORLEVEL%"

echo.
pause
exit /b %RC%
