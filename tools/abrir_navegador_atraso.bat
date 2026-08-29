@echo off
REM Aguarda Flask subir e abre o painel no navegador padrao
setlocal EnableDelayedExpansion

set "URL=%~1"
if "%URL%"=="" set "URL=http://192.168.16.130:15000/dashboard"

set "URL=%URL:"=%"
set "URL=%URL: =%"

echo.%URL%| findstr /i /r "^https\?://" >nul || set "URL=http://192.168.16.130:15000/dashboard"
echo.%URL%| findstr /i /r "/[a-z]" >nul || set "URL=%URL%/dashboard"

call "%~dp0encontrar_python.bat"
set "PY=%ELEVA_PYTHON%"

set /a TENTATIVAS=0
:espera
set /a TENTATIVAS+=1
if !TENTATIVAS! GTR 45 goto abrir

if defined PY (
    "%PY%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:15000/dashboard', timeout=3)" 2>nul && goto abrir
) else (
    powershell -NoProfile -Command "try{(Invoke-WebRequest -Uri 'http://127.0.0.1:15000/dashboard' -UseBasicParsing -TimeoutSec 3).StatusCode; exit 0}catch{exit 1}" 2>nul && goto abrir
)

timeout /t 2 /nobreak >nul
goto espera

:abrir
start "" "%URL%"
exit /b 0
