@echo off
title ELEVA LOCKER - Validar portas Bancada
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
echo   VALIDAR PORTAS BANCADA (24 portas)
echo ============================================================
echo.
echo  [1] Listar mapeamento
echo  [2] Amostra: abrir #1, #9, #17 (1 por ESP)
echo  [3] Ler sensores das 3 ESPs
echo  [4] Abrir UMA porta (digite o numero)
echo  [5] Abrir TODAS 1..24 (sequencia)
echo.

set /p OPC="Opcao [2]: "
if "%OPC%"=="" set "OPC=2"

if "%OPC%"=="1" "%PYTHON%" tools\validar_portas_bancada.py --listar
if "%OPC%"=="2" "%PYTHON%" tools\validar_portas_bancada.py --amostra
if "%OPC%"=="3" "%PYTHON%" tools\validar_portas_bancada.py --sensores
if "%OPC%"=="4" (
    set /p NUM="Numero do compartimento (1-24): "
    "%PYTHON%" tools\validar_portas_bancada.py --abrir !NUM!
)
if "%OPC%"=="5" (
    echo ATENCAO: vai acionar os 24 reles em sequencia.
    pause
    "%PYTHON%" tools\validar_portas_bancada.py --todas --confirmar
)

echo.
pause
