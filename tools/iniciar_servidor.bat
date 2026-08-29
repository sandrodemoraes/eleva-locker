@echo off
title ELEVA LOCKER - Servidor
cd /d C:\ElevaLocker
if errorlevel 1 (
    echo.
    echo ERRO: pasta C:\ElevaLocker nao encontrada.
    echo Ajuste o caminho neste .bat se o projeto estiver em outro lugar.
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
        echo ERRO: Python nao encontrado. Instale Python 3 e marque "Add to PATH".
        pause
        exit /b 1
    )
    set PY=python
) else (
    set PY=py
)

echo Iniciando servidor em http://0.0.0.0:15000 ...
echo Totem: http://192.168.16.130:15000/totem/2
echo.
echo DEIXE ESTA JANELA ABERTA. Fechar = servidor para.
echo.

%PY% app.py
if errorlevel 1 (
    echo.
    echo === Servidor encerrou com erro ===
    echo Se apareceu ModuleNotFoundError, rode: tools\atualizar_totem.bat
    pause
    exit /b 1
)

pause
