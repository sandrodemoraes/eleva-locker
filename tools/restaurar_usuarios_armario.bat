@echo off
title ELEVA LOCKER - Restaurar Usuarios do Armario
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
echo  RESTAURAR USUARIOS DO ARMARIO
echo  Quando sumirem em Armarios -^> Matriz -^> Usuarios
echo  ==================================================
echo.

%PYTHON% tools\restaurar_usuarios_armario.py %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" echo  Se ainda vazio, cadastre operadores na pagina do armario.
pause
exit /b %RC%
