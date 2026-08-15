@echo off
REM Aguarda Flask local e abre painel VERDE (IP bancada — nunca APP_URL_BASE publico)
setlocal
set "URL=%~1"
if "%URL%"=="" set "URL=http://192.168.16.130:15000/dashboard"

echo.%URL%| findstr /i /r "^https\?://" >nul || set "URL=http://192.168.16.130:15000/dashboard"

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"

REM Para container Docker antigo (tela azul) liberar porta 15000
docker stop elevalocker-web-1 2>nul
docker rm -f elevalocker-web-1 2>nul

set /a TENTATIVAS=0
:espera
set /a TENTATIVAS+=1
if %TENTATIVAS% GTR 40 goto abrir_mesmo_assim

if defined PYTHON (
    %PYTHON% -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:15000/dashboard', timeout=3)" 2>nul && goto abrir
) else (
    powershell -NoProfile -Command "try{(Invoke-WebRequest -Uri 'http://127.0.0.1:15000/dashboard' -UseBasicParsing -TimeoutSec 3).StatusCode; exit 0}catch{exit 1}" 2>nul && goto abrir
)

timeout /t 2 /nobreak >nul
goto espera

:abrir
start "" "%URL%"
exit /b 0

:abrir_mesmo_assim
start "" "%URL%"
exit /b 0
