@echo off
title ELEVA LOCKER - Criar atalhos
color 0A
cd /d "%~dp0.."

echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_desktop.ps1"
set "ERR=%ERRORLEVEL%"

echo.
if not "%ERR%"=="0" (
    echo ERRO: Nao foi possivel criar os atalhos.
    echo.
    pause
    exit /b 1
)

echo Para remover o inicio automatico, execute:
echo   tools\remover_inicio_windows.bat
echo.
pause
