@echo off
title ELEVA LOCKER - Totem Kiosk (Chrome)
setlocal
REM Uso: tools\atalho_totem_kiosk.bat [armario_id]
REM Ex.: tools\atalho_totem_kiosk.bat 2   (Matriz)
REM      tools\atalho_totem_kiosk.bat 3   (Bancada)

set "ARM=%~1"
if "%ARM%"=="" set "ARM=3"
set "TOTEM_URL=http://192.168.16.130:15000/totem/%ARM%?_=%RANDOM%"

set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME%" (
    echo Chrome nao encontrado. Abrindo no navegador padrao:
    echo   %TOTEM_URL%
    start "" "%TOTEM_URL%"
    pause
    exit /b 1
)

start "" "%CHROME%" --kiosk --app=%TOTEM_URL%
echo Totem kiosk armario %ARM% — %TOTEM_URL%
echo Alt+F4 ou Ctrl+W para fechar.
