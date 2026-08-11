@echo off
title ELEVA LOCKER - Atalho Totem Kiosk (Chrome)
REM Edite TOTEM_URL se o IP ou armario mudar
set "TOTEM_URL=http://192.168.16.130:15000/totem/3"

set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"

if not exist "%CHROME%" (
    echo Chrome nao encontrado. Abra manualmente:
    echo   %TOTEM_URL%
    start "" "%TOTEM_URL%"
    pause
    exit /b 1
)

start "" "%CHROME%" --kiosk --app=%TOTEM_URL%
echo Totem kiosk aberto. Alt+F4 ou Ctrl+W para fechar.
