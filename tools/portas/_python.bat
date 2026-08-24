@echo off
cd /d "%~dp0..\.."
set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    exit /b 1
)
