@echo off
title ELEVA LOCKER - Remover inicio automatico
cd /d "%~dp0.."

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "ATALHO=%STARTUP%\ELEVA LOCKER - Iniciar.lnk"
set "DESKTOP=%USERPROFILE%\Desktop\ELEVA LOCKER.lnk"

echo Removendo atalhos ELEVA LOCKER...
echo.

if exist "%ATALHO%" (
    del "%ATALHO%"
    echo OK  Startup removido
) else (
    echo --  Nenhum atalho na pasta Inicializar
)

for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D\ELEVA LOCKER.lnk"
if exist "%DESKTOP%" (
    del "%DESKTOP%"
    echo OK  Area de Trabalho removido
)

schtasks /Delete /TN "ELEVA LOCKER - Iniciar" /F 2>nul
if not errorlevel 1 echo OK  Tarefa agendada removida

echo.
echo Para recriar: tools\instalar_inicio_windows.bat
echo.
pause
