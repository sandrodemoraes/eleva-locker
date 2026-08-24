@echo off
title ELEVA LOCKER — Validar portas
cd /d "%~dp0..\.."
call "%~dp0_config.bat"
call "%~dp0_python.bat"

echo Validar armario id=%ARMARIO_ID%
echo.
echo  [1] Listar mapeamento compartimento -^> ESP -^> rele
echo  [2] Abrir amostra (1a porta de cada ESP)
echo  [3] Ler sensores
echo.

set /p OPC="Opcao [1]: "
if "%OPC%"=="" set "OPC=1"

if "%OPC%"=="1" %PYTHON% tools\validar_portas_bancada.py --armario-id %ARMARIO_ID% --listar
if "%OPC%"=="2" %PYTHON% tools\validar_portas_bancada.py --armario-id %ARMARIO_ID% --amostra
if "%OPC%"=="3" %PYTHON% tools\validar_portas_bancada.py --armario-id %ARMARIO_ID% --sensores

echo.
pause
