@echo off
title ELEVA LOCKER - Backup Disco D
color 0E
cd /d "%~dp0.."

call "%~dp0encontrar_python.bat"
set "PY=%ELEVA_PYTHON%"

if not defined PY (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo.
echo  BACKUP DISCO D: — banco + .env + espelho projeto
echo  =================================================
echo.

"%PY%" tools\backup_disco_d.py
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo Backup salvo em D:\ElevaLockerBackup\
) else (
    echo ERRO no backup — codigo %RC%
)
pause
exit /b %RC%
