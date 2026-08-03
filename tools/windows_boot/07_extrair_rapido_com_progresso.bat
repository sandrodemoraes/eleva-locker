@echo off
REM Extracao rapida COM progresso (nao fica mudo).
REM Uso:
REM   07_extrair_rapido_com_progresso.bat
REM   07_extrair_rapido_com_progresso.bat "D:\backup pc fabio" "D:\Recuperado_Windows_Antigo"

setlocal
set "ORIG=%~1"
set "DEST=%~2"
if "%ORIG%"=="" set "ORIG=D:\backup pc fabio"
if "%DEST%"=="" set "DEST=D:\Recuperado_Windows_Antigo"

echo Fechando a extracao antiga se estiver travada: Ctrl+C na outra janela.
echo.
echo Origem: %ORIG%
echo Destino: %DEST%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp007_extrair_rapido_com_progresso.ps1" -OrigParent "%ORIG%" -Dest "%DEST%"
echo.
pause
endlocal
