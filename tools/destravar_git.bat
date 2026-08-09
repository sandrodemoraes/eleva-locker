@echo off
title ELEVA LOCKER - Destravar Git e Atualizar
color 0A
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo.
echo  DESTRAVAR GIT + ATUALIZAR MATRIZ
echo  ================================
echo.
echo  Problema comum: git pull bloqueado pelo firmware .ino local
echo.

if not exist "backups" mkdir backups

echo [1] Backup manual do firmware (WiFi/token)...
if exist "firmware\elevalocker_sync\elevalocker_sync.ino" (
    copy /Y "firmware\elevalocker_sync\elevalocker_sync.ino" "backups\_pre_update_firmware.ino"
    echo     OK backups\_pre_update_firmware.ino
) else (
    echo     AVISO: .ino nao encontrado
)

echo.
echo [2] Git stash (guardar alteracoes locais)...
git stash push -m "eleva-pre-atualizar-matriz"
if errorlevel 1 (
    echo     AVISO: stash falhou ou nada para guardar — continuando
)

echo.
echo [3] Git pull...
git pull origin cursor/fix-retirada-rele-c05c
if errorlevel 1 (
    echo.
    echo ERRO: git pull falhou. Veja acima.
    pause
    exit /b 1
)

echo.
echo [4] Atualizar Matriz (backup + setup + reinicio)...
if exist "tools\atualizar_matriz.bat" (
    call tools\atualizar_matriz.bat
) else (
    %PYTHON% tools\atualizar_matriz.py
)

echo.
echo WiFi/token do firmware antigo: backups\_pre_update_firmware.ino
echo Copie WIFI_SSID, WIFI_PASSWORD e ESP32_TOKEN para o .ino novo se necessario.
echo.
pause
