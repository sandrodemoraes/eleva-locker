@echo off
title ELEVA LOCKER - Visual Verde + Bancada
color 0A
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
echo  VISUAL VERDE — so atualiza codigo (nao mexe em usuarios)
echo  Se armario sumiu: tools\consertar_bancada.bat
echo  Com consertar:    atualizar_visual_verde.py --com-consertar
echo  =====================================
echo.

%PYTHON% tools\atualizar_visual_verde.py
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" echo  FALHOU — mande print desta tela.
pause
exit /b %RC%
