@echo off
title ELEVA LOCKER - Backup Firmware ESP (.ino) no D:
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
echo  BACKUP FIRMWARE ESP — copia .ino de cada placa para D:
echo  =======================================================
echo.

%PYTHON% tools\backup_firmware_esp.py %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" (
    echo  Falhou — veja mensagens acima.
) else (
    echo  Pronto! Veja D:\ElevaLockerBackup\firmware\
)
pause
exit /b %RC%
