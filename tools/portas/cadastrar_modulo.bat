@echo off
setlocal enabledelayedexpansion
title ELEVA LOCKER — Cadastrar modulo ESP
cd /d "%~dp0..\.."
call "%~dp0_config.bat"
call "%~dp0_python.bat"

echo ============================================================
echo   Cadastrar ESP — armario id=%ARMARIO_ID%
echo ============================================================
echo.
echo   Modulo   Portas      IP sugerido
echo   M1       #1-8        %IP_M1%
echo   M2       #9-16       %IP_M2%
echo   M3       #17-24      %IP_M3%
echo   M4       #25-32      %IP_M4%
echo   M5       #33-40      %IP_M5%
echo   M6       #41-48      %IP_M6%
echo   M7       #49-56      %IP_M7%
echo   M8       #57-64      %IP_M8%
echo.

set /p MOD="Modulo (1-8): "
if "%MOD%"=="" goto :fim

set "PORTA_INI=1"
set "NOME=ESP M1"
set "IP_PAD=%IP_M1%"
set "TOTAL=8"

if "%MOD%"=="2" set "PORTA_INI=9" & set "NOME=ESP M2" & set "IP_PAD=%IP_M2%" & set "TOTAL=16"
if "%MOD%"=="3" set "PORTA_INI=17" & set "NOME=ESP M3" & set "IP_PAD=%IP_M3%" & set "TOTAL=24"
if "%MOD%"=="4" set "PORTA_INI=25" & set "NOME=ESP M4" & set "IP_PAD=%IP_M4%" & set "TOTAL=32"
if "%MOD%"=="5" set "PORTA_INI=33" & set "NOME=ESP M5" & set "IP_PAD=%IP_M5%" & set "TOTAL=32"
if "%MOD%"=="6" set "PORTA_INI=41" & set "NOME=ESP M6" & set "IP_PAD=%IP_M6%" & set "TOTAL=64"
if "%MOD%"=="7" set "PORTA_INI=49" & set "NOME=ESP M7" & set "IP_PAD=%IP_M7%" & set "TOTAL=64"
if "%MOD%"=="8" set "PORTA_INI=57" & set "NOME=ESP M8" & set "IP_PAD=%IP_M8%" & set "TOTAL=64"

set /p IP_ESP="IP da ESP [%IP_PAD%]: "
if "%IP_ESP%"=="" set "IP_ESP=%IP_PAD%"

set /p NOME_ESP="Nome no painel [%NOME%]: "
if "%NOME_ESP%"=="" set "NOME_ESP=%NOME%"

set /p TOTAL_IN="Total portas do armario [%TOTAL%]: "
if not "%TOTAL_IN%"=="" set "TOTAL=%TOTAL_IN%"

echo.
echo Cadastrando %NOME_ESP% IP=%IP_ESP% portas #%PORTA_IN%...
%PYTHON% tools\cadastrar_esp_nova.py --ip-esp %IP_ESP% --nome-esp "%NOME_ESP%" --armario-id %ARMARIO_ID% --porta-inicial %PORTA_INI% --portas 8 --max-portas-armario %TOTAL% --servidor %SERVIDOR%

echo.
echo Depois: grave firmware com o TOKEN impresso acima.

:fim
echo.
pause
endlocal
