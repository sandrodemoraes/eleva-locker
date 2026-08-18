@echo off
title ELEVA LOCKER - Atualizar todos os totens
color 0A
cd /d "%~dp0.."

set "BASE=http://192.168.16.130:15000"
set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"

echo ============================================================
echo   ATUALIZAR TOTENS (Matriz + Bancada — mesmo modelo)
echo ============================================================
echo.
echo  Todos os armarios usam o MESMO totem.html + totem.css
echo  URL: /totem/2  (Matriz)   /totem/3  (Bancada)
echo.

if exist .git (
    echo [1] git pull...
    git pull
    echo.
)

echo [2] Versao do servidor:
if defined PYTHON (
    %PYTHON% -c "import urllib.request; r=urllib.request.urlopen('%BASE%/totem/versao', timeout=5); print(r.read().decode())" 2>nul
) else (
    echo   Abra: %BASE%/totem/versao
)
echo.

echo [3] Reinicie o servidor se acabou de dar pull:
echo     iniciar_elevalocker.bat
echo.

echo [4] Abrindo totens (Ctrl+F5 se layout antigo)...
start "" "%BASE%/totem/2?_=%RANDOM%"
timeout /t 1 /nobreak >nul
start "" "%BASE%/totem/3?_=%RANDOM%"

echo.
echo  Canto superior direito deve mostrar v2.4.7 ou superior.
echo.
pause
