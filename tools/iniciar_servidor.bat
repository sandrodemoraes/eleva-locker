@echo off
title ELEVA LOCKER - Servidor (bancada)
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

echo Parando servidor antigo...
%PYTHON% tools\parar_servidor.py nopause 2>nul

set ELEVA_BANCADA=1
set DATABASE_URL=

echo.
echo ============================================================
echo   ELEVA LOCKER — servidor bancada (SQLite)
echo   NAO feche esta janela
echo ============================================================
echo.

%PYTHON% app.py
pause
