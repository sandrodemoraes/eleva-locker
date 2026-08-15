@echo off
title ELEVA LOCKER - Remover inicio automatico

set "ATALHO=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ELEVA LOCKER - Iniciar.lnk"

if exist "%ATALHO%" (
    del "%ATALHO%"
    echo Atalho removido da pasta Inicializar.
) else (
    echo Nenhum atalho ELEVA LOCKER encontrado na pasta Inicializar.
)

echo.
pause
