@echo off
title ELEVA LOCKER - Reparar atalhos Windows
color 0A
cd /d "%~dp0.."

echo ============================================================
echo   REPARAR ATALHO + INICIO DO WINDOWS
echo ============================================================
echo.
echo  Problema comum: atalho aponta para cmd.exe sem argumentos
echo                  ou pasta errada (servidor nao sobe ao ligar PC)
echo.
echo  Pasta atual: %CD%
echo.

call "%~dp0instalar_inicio_windows.bat"
