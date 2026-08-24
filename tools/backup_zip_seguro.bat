@echo off
title ELEVA LOCKER - Backup ZIP Seguro
color 0A
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
echo  BACKUP ZIP SEGURO — codigo + banco + .env
echo  ==========================================
echo  Salva em: D:\ElevaLockerBackup\zip\
echo.

"%PYTHON%" tools\backup_zip_seguro.py %*
set "RC=%ERRORLEVEL%"

echo.
pause
exit /b %RC%
