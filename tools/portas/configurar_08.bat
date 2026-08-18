@echo off
title ELEVA LOCKER — 8 portas
cd /d "%~dp0..\.."
call "%~dp0_config.bat"
call "%~dp0_python.bat"

echo Configurando armario id=%ARMARIO_ID% com 8 portas (1 x ESP 8ch)...
echo.
%PYTHON% tools\configurar_portas_armario.py --armario-id %ARMARIO_ID% --portas 8
echo.
pause
