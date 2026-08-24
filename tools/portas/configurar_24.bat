@echo off
title ELEVA LOCKER — 24 portas
cd /d "%~dp0..\.."
call "%~dp0_config.bat"
call "%~dp0_python.bat"

echo Configurando armario id=%ARMARIO_ID% com 24 portas (3 x ESP 8ch)...
echo  M1: #1-8   M2: #9-16   M3: #17-24
echo.
%PYTHON% tools\configurar_portas_armario.py --armario-id %ARMARIO_ID% --portas 24
echo.
pause
