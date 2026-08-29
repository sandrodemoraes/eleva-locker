@echo off
title ELEVA LOCKER - Backup ZIP Disco D
cd /d "%~dp0.."
call "%~dp0encontrar_python.bat"
if not defined ELEVA_PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)
"%ELEVA_PYTHON%" tools\backup_zip_seguro.py
pause
