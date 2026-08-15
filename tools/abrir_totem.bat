@echo off
title ELEVA LOCKER - Abrir Totem
setlocal EnableDelayedExpansion
cd /d "%~dp0.."

set "BASE=http://192.168.16.130:15000"
set "V=2.4.7"

echo ============================================================
echo   TOTEM — mesmo layout para todos os armarios
echo ============================================================
echo.
echo   Matriz (id 2):  %BASE%/totem/2
echo   Bancada (id 3): %BASE%/totem/3
echo.
echo  [1] Matriz  /totem/2
echo  [2] Bancada /totem/3
echo  [3] Abrir os dois (2 abas)
echo  [4] Outro id
echo.

set /p OPC="Opcao [3]: "
if "%OPC%"=="" set "OPC=3"

if "%OPC%"=="1" (
    start "" "%BASE%/totem/2?_=%V%"
    goto fim
)
if "%OPC%"=="2" (
    start "" "%BASE%/totem/3?_=%V%"
    goto fim
)
if "%OPC%"=="3" (
    start "" "%BASE%/totem/2?_=%V%"
    timeout /t 1 /nobreak >nul
    start "" "%BASE%/totem/3?_=%V%"
    goto fim
)
if "%OPC%"=="4" (
    set /p AID="ID do armario: "
    start "" "%BASE%/totem/!AID!?_=%V%"
    goto fim
)

echo Opcao invalida.
pause
exit /b 1

:fim
echo.
echo  Totem aberto. Se layout antigo: Ctrl+F5 no navegador.
echo  Versao esperada no canto: %V%
echo.
pause
