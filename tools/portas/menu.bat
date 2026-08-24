@echo off
title ELEVA LOCKER — Portas do armario (8 a 64)
color 0A
cd /d "%~dp0..\.."
call "%~dp0_config.bat"
call "%~dp0_python.bat"

echo ============================================================
echo   ELEVA LOCKER — Configurar portas do armario
echo   Armario padrao: id=%ARMARIO_ID%  ^|  Servidor: %SERVIDOR%
echo   Pasta: tools\portas\
echo ============================================================
echo.
echo   [1]  8 portas   (1 ESP)
echo   [2] 16 portas   (2 ESPs)
echo   [3] 24 portas   (3 ESPs)
echo   [4] 32 portas   (4 ESPs)
echo   [5] 64 portas   (8 ESPs)
echo.
echo   [6] Listar armarios cadastrados
echo   [7] Validar portas (mapeamento + teste)
echo   [8] Cadastrar ESP nova (modulo)
echo   [9] Abrir painel do armario no navegador
echo   [0] Sair
echo.
echo   Edite ARMARIO_ID em tools\portas\_config.bat se necessario.
echo.

set /p OPC="Opcao: "
if "%OPC%"=="1" call "%~dp0configurar_08.bat"
if "%OPC%"=="2" call "%~dp0configurar_16.bat"
if "%OPC%"=="3" call "%~dp0configurar_24.bat"
if "%OPC%"=="4" call "%~dp0configurar_32.bat"
if "%OPC%"=="5" call "%~dp0configurar_64.bat"
if "%OPC%"=="6" call "%~dp0listar_armarios.bat"
if "%OPC%"=="7" call "%~dp0validar.bat"
if "%OPC%"=="8" call "%~dp0cadastrar_modulo.bat"
if "%OPC%"=="9" start "" "%SERVIDOR%/armarios/%ARMARIO_ID%"
if "%OPC%"=="0" exit /b 0

echo.
pause
