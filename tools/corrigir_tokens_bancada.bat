@echo off
title ELEVA LOCKER - Corrigir tokens ESP
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo.
echo  CORRIGIR TOKENS ESP (403 Token rejeitado)
echo  ========================================
echo.

%PYTHON% tools\corrigir_tokens_bancada.py %*
set "RC=%ERRORLEVEL%"
echo.
pause
exit /b %RC%
