@echo off
title ELEVA LOCKER - Bancada 24 portas
color 0A
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo ============================================================
echo   BANCADA 24 PORTAS (3 x ESP 8ch)
echo ============================================================
echo.
echo  1. Faca backup antes: tools\backup_obrigatorio.bat
echo  2. Este script ajusta o armario e ressincroniza ESPs existentes
echo  3. Depois cadastre ESP M2 e M3 com cadastrar_esp_nova.bat
echo.

set /p ARM_ID="ID do armario [2]: "
if "%ARM_ID%"=="" set "ARM_ID=2"

set /p TOTAL="Total de portas (8/16/24/32/64) [16]: "
if "%TOTAL%"=="" set "TOTAL=16"

echo.
%PYTHON% tools\configurar_portas_armario.py --armario-id %ARM_ID% --portas %TOTAL% 2>nul
if errorlevel 1 %PYTHON% tools\configurar_bancada_24_portas.py --armario-id %ARM_ID% --portas %TOTAL%

echo.
pause
