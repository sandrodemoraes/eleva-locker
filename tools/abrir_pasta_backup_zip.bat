@echo off
title ELEVA LOCKER - Pasta dos backups ZIP
set "PASTA=D:\ElevaLockerBackup\zip"

if not exist "D:\" (
    echo Disco D: nao encontrado.
    set "PASTA=%~dp0..\backups\zip"
)

if not exist "%PASTA%" (
    echo Pasta ainda nao existe: %PASTA%
    echo Rode antes: tools\backup_zip_seguro.bat
    pause
    exit /b 1
)

echo.
echo Backups ZIP em:
echo   %PASTA%
echo.
dir /o-d "%PASTA%\*.zip" 2>nul
if errorlevel 1 (
    echo Nenhum .zip encontrado. Rode: tools\backup_zip_seguro.bat
) else (
    echo.
    echo Abrindo pasta no Explorer...
    start "" explorer "%PASTA%"
)
echo.
pause
