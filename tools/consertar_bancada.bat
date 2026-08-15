@echo off
title ELEVA LOCKER - CONSERTAR BANCADA
color 0C
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
echo  CONSERTAR BANCADA — SQLite + armario + totem + token
echo  Use isto quando voltar erro de armario 0 ou totem sem configurar
echo  ======================================================
echo.

%PYTHON% tools\consertar_bancada.py %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" echo  FALHOU — mande print desta tela.
pause
exit /b %RC%
