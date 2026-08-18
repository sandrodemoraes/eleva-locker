@echo off
title ELEVA LOCKER — 32 portas
cd /d "%~dp0..\.."
call "%~dp0_config.bat"
call "%~dp0_python.bat"

echo Configurando armario id=%ARMARIO_ID% com 32 portas (4 x ESP 8ch)...
echo  M1: #1-8   M2: #9-16   M3: #17-24   M4: #25-32
echo.
%PYTHON% tools\configurar_portas_armario.py --armario-id %ARMARIO_ID% --portas 32
echo.
pause
