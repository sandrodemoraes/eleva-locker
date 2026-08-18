@echo off
title ELEVA LOCKER — Listar armarios
cd /d "%~dp0..\.."
call "%~dp0_python.bat"

%PYTHON% tools\configurar_portas_armario.py --listar
echo.
pause
