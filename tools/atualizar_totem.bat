@echo off
title ELEVA LOCKER - Atualizar totem v2
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

echo Parando container Docker web (imagem antiga na porta 15000)...
docker stop elevalocker-web-1 2>nul

echo.
%PYTHON% tools\atualizar_totem.py

echo.
pause
