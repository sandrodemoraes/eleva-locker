@echo off
title ELEVA LOCKER - Atualizar e iniciar
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

echo Atualizando codigo...
git pull origin cursor/fix-retirada-rele-c05c
if errorlevel 1 (
    echo AVISO: git pull falhou — iniciando mesmo assim.
)

call "%~dp0iniciar_tudo.bat"
