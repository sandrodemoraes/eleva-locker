@echo off
title ELEVA LOCKER - Remover inicio automatico
color 0C

echo ============================================================
echo      ELEVA LOCKER - Remover inicio automatico com Windows
echo ============================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0remover_inicio_windows.ps1"

echo.
echo O atalho da area de trabalho NAO foi removido.
echo.
pause
