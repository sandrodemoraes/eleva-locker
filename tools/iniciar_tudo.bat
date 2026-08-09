@echo off
title ELEVA LOCKER - Iniciar servicos
color 0B
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

echo Usando: %PYTHON%
echo.

%PYTHON% tools\iniciar_tudo.py
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Servidor ELEVA LOCKER — porta 15000
echo   Mantenha ESTA janela aberta
echo   Ctrl+C para parar o servidor
echo ============================================================
echo.

REM Bancada: SQLite obrigatorio (nao usar Postgres do Docker)
set ELEVA_BANCADA=1
set DATABASE_URL=

%PYTHON% app.py

pause
