@echo off
title ELEVA LOCKER - Lembretes encomenda 24h
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo Reenviando lembretes para encomendas com mais de 24h no armario...
%PYTHON% tools\lembretes_encomenda.py
echo.
pause
