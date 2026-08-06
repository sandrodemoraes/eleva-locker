@echo off
title ELEVA LOCKER - Subir servidor NOVO
color 0A
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"

echo.
echo  SUBIR SERVIDOR NOVO (python app.py)
echo  ===================================
echo.

echo [1] Matando Docker antigo...
docker stop elevalocker-web-1 2>nul
docker rm -f elevalocker-web-1 2>nul
docker compose stop web 2>nul

echo [2] Liberando porta 15000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":15000" ^| findstr "LISTENING"') do (
    echo     PID %%a
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak >nul

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo [3] Iniciando python app.py...
echo     Deve aparecer: ELEVA LOCKER — Totem v2.3.3
echo.
%PYTHON% app.py

pause
