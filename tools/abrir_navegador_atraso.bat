@echo off
REM Abre dashboard no navegador apos 6 segundos
set "URL=%~1"
if "%URL%"=="" set "URL=http://localhost:15000/dashboard"
echo.%URL%| findstr /i /r "^https\?://" >nul || set "URL=http://localhost:15000/dashboard"
timeout /t 6 /nobreak >nul
start "" "%URL%"
