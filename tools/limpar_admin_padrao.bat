@echo off
title ELEVA LOCKER - Limpar admin padrao
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
echo  Remove admin@elevalocker.com (123456)
echo  Mantem sandro.demoraes@gmail.com como Administrador
echo  Para TROCAR SENHA use: tools\limpar_admin_sandro.bat
echo  =============================================
echo.

%PYTHON% tools\limpar_admin_padrao.py %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" echo  FALHOU — mande print desta tela.
pause
exit /b %RC%
