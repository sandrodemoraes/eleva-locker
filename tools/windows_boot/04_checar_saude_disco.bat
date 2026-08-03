@echo off
REM Checa saude da particao Windows.
REM Uso: 04_checar_saude_disco.bat W
REM   W = letra da particao Windows

setlocal
set "WINLETTER=%~1"
if "%WINLETTER%"=="" (
    echo Uso: 04_checar_saude_disco.bat LETRA
    echo Exemplo: 04_checar_saude_disco.bat D
    pause
    exit /b 1
)

set "WINLETTER=%WINLETTER::=%"
set "WINDIR=%WINLETTER%:\Windows"

if not exist "%WINDIR%\System32\ntoskrnl.exe" (
    echo ERRO: %WINDIR% nao parece ser uma instalacao Windows.
    pause
    exit /b 1
)

echo ============================================================
echo  chkdsk + sfc offline em %WINLETTER%:
echo  Pode demorar HORAS. Nao desligue o PC.
echo ============================================================
pause

chkdsk %WINLETTER%: /f /r
sfc /scannow /offbootdir=%WINLETTER%:\ /offwindir=%WINDIR%

echo.
echo Concluido.
pause
endlocal
