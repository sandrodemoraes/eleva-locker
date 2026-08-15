@echo off
title ELEVA LOCKER - Corrigir seguranca do .env
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
echo  CORRIGIR .env — SECRET_KEY, WhatsApp key, FLASK_DEBUG, PIN fraco
echo  Faz backup antes de alterar
echo.
echo  Simular primeiro:  corrigir_env_seguranca.py --simular
echo.

%PYTHON% tools\corrigir_env_seguranca.py %*
pause
