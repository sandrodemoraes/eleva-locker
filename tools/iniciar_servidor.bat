@echo off
title ELEVA LOCKER - Servidor
setlocal

REM Pasta do projeto = pai de tools\ (funciona em qualquer disco/caminho)
set "PROJETO=%~dp0.."
cd /d "%PROJETO%"
if not exist "app.py" (
    echo.
    echo ERRO: app.py nao encontrado em:
    echo   %CD%
    echo.
    echo Abra o atalho correto ou rode este .bat de dentro da pasta tools do ElevaLocker.
    pause
    exit /b 1
)

echo.
echo === ELEVA LOCKER ===
echo Pasta: %CD%
echo.

where py >nul 2>&1
if errorlevel 1 (
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERRO: Python nao encontrado.
        echo Instale Python 3 em python.org e marque "Add Python to PATH".
        pause
        exit /b 1
    )
    set "PY=python"
) else (
    set "PY=py"
)

echo Python: %PY%
echo URL totem: http://192.168.16.130:15000/totem/2
echo.
echo DEIXE ESTA JANELA ABERTA. Fechar = servidor para.
echo.

%PY% app.py
set "COD=%ERRORLEVEL%"
if not "%COD%"=="0" (
    echo.
    echo === Servidor encerrou com erro (codigo %COD%) ===
    echo Se ModuleNotFoundError: tools\atualizar_totem.bat
)
echo.
pause
exit /b %COD%
