@echo off
title ELEVA LOCKER - Recriar Matriz
cd /d "%~dp0.."
echo.
echo === Recriar ELEVA Locker Matriz no banco ===
py tools\recriar_matriz_armario.py
echo.
pause
