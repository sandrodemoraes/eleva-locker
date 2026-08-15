@echo off
title ELEVA LOCKER - Admin Sandro + nova senha
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

echo.
echo  Remove admin@elevalocker.com
echo  Mantem sandro.demoraes@gmail.com como Administrador
echo  Voce vai digitar a NOVA SENHA (nao aparece na tela)
echo  ====================================================
echo.

%PYTHON% tools\limpar_admin_padrao.py --alterar-senha %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" echo  FALHOU — mande print desta tela.
pause
exit /b %RC%
