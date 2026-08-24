@echo off
title ELEVA LOCKER — 16 portas
cd /d "%~dp0..\.."
call "%~dp0_config.bat"
call "%~dp0_python.bat"

echo Configurando armario id=%ARMARIO_ID% com 16 portas (2 x ESP 8ch)...
echo  M1: #1-8   M2: #9-16
echo.
%PYTHON% tools\configurar_portas_armario.py --armario-id %ARMARIO_ID% --portas 16
echo.
pause
