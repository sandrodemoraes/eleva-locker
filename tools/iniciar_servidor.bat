@echo off
setlocal EnableDelayedExpansion
title ELEVA LOCKER - Servidor

set "PROJETO=%~dp0.."
cd /d "%PROJETO%"
if not exist "app.py" (
    echo ERRO: app.py nao encontrado em %CD%
    pause
    exit /b 1
)

if not exist "logs" mkdir logs
set "LOG=logs\servidor_%date:~-4%%date:~3,2%%date:~0,2%.log"
echo [%date% %time%] Inicio em %CD%>> "%LOG%"

call "%~dp0encontrar_python.bat"
set "PY=%ELEVA_PYTHON%"

if not defined PY (
    echo ERRO: Python nao encontrado.>> "%LOG%"
    echo.
    echo ERRO: Python nao encontrado.
    echo Instale Python 3 e marque "Add Python to PATH".
    echo Log: %CD%\%LOG%
    pause
    exit /b 1
)

echo.
echo === ELEVA LOCKER ===
echo Pasta:  %CD%
echo Python: %PY%
echo Log:    %LOG%
echo Totem:  http://192.168.16.130:15000/totem/2
echo.
echo DEIXE ESTA JANELA ABERTA. Fechar = servidor para.
echo Ctrl+C pergunta S/N (N = reinicia).
echo.

if /i not "%ELEVA_SEM_NAVEGADOR%"=="1" (
    set "PAINEL=http://192.168.16.130:15000/dashboard"
    for /f "usebackq tokens=1,* delims==" %%a in (`findstr /i /b "ELEVA_PAINEL_URL=" .env 2^>nul`) do (
        set "PAINEL=%%b"
        set "PAINEL=!PAINEL: =!"
    )
    echo Abrindo navegador em !PAINEL! ...
    start /B "" "%~dp0abrir_navegador_atraso.bat" "!PAINEL!"
)

:loop
echo [%date% %time%] Subindo app.py>> "%LOG%"
"%PY%" -u app.py 2>&1
set "COD=%ERRORLEVEL%"
echo [%date% %time%] Saiu codigo %COD%>> "%LOG%"

if not "%COD%"=="0" (
    echo.
    echo === Erro codigo %COD% ===
    echo Veja %LOG%
    pause
    exit /b %COD%
)

echo.
choice /C SN /M "Encerrar o servidor ELEVA LOCKER (N=reinicia)"
if errorlevel 2 (
    echo Reiniciando...
    goto loop
)

echo Servidor encerrado.
pause
exit /b 0
