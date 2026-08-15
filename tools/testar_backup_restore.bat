@echo off
title ELEVA LOCKER - Testar Backup / Restore
color 0B
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
echo  TESTE BACKUP / RESTORE — ELEVA LOCKER
echo  ======================================
echo.

%PYTHON% tools\testar_backup_restore.py %*
set "RC=%ERRORLEVEL%"

echo.
pause
exit /b %RC%
