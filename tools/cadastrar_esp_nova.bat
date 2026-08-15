@echo off
title ELEVA LOCKER - Cadastrar ESP nova
color 0A
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo ============================================================
echo   CADASTRAR ESP32 NOVA (mesmo padrao da Matriz)
echo ============================================================
echo.
echo  Antes: conecte a ESP no Wi-Fi e descubra o IP
echo         (roteador, Serial Monitor ou ping)
echo.
echo  Exemplo:
echo    %PYTHON% tools\cadastrar_esp_nova.py --ip-esp 192.168.16.105
echo.
echo  Segunda bancada (armario novo):
echo    %PYTHON% tools\cadastrar_esp_nova.py --ip-esp 192.168.16.105 --criar-armario
echo.
echo  No armario Matriz existente (id=2):
echo    %PYTHON% tools\cadastrar_esp_nova.py --ip-esp 192.168.16.105 --armario-id 2 --nome-esp "ESP Matriz reserva"
echo.

set /p IP_ESP="IP da ESP nova: "
if "%IP_ESP%"=="" (
    echo IP obrigatorio.
    pause
    exit /b 1
)

set /p NOME_ESP="Nome no painel [ESP Bancada 2]: "
if "%NOME_ESP%"=="" set "NOME_ESP=ESP Bancada 2"

echo.
echo Cadastrando...
%PYTHON% tools\cadastrar_esp_nova.py --ip-esp %IP_ESP% --nome-esp "%NOME_ESP%" --criar-armario

echo.
pause
