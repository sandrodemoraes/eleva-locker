@echo off
REM Cria atalho na Area de Trabalho (wrapper)
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_desktop.ps1"
echo.
pause
