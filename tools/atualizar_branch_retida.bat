@echo off
title ELEVA LOCKER - Atualizar branch retida (seguro)
color 0A
cd /d "%~dp0.."

set "BRANCH=cursor/retirada-pacote-retido-c05c"
set "BACKUP=D:\ElevaLockerBackup\git_update"

echo ============================================================
echo   ATUALIZAR CODIGO — %BRANCH%
echo   Preserva: database\elevalocker.db + tokens do firmware
echo ============================================================
echo.
pause

if not exist "%BACKUP%" mkdir "%BACKUP%"

echo [1] Backup banco + firmware...
copy /y database\elevalocker.db "%BACKUP%\elevalocker.db.bak" >nul
copy /y firmware\elevalocker_sync\elevalocker_sync.ino "%BACKUP%\elevalocker_sync.ino.bak" >nul
echo      Salvo em %BACKUP%

echo [2] Abortar merge pendente...
git merge --abort 2>nul

echo [3] Buscar GitHub...
git fetch origin %BRANCH%
if errorlevel 1 (
    echo ERRO no fetch.
    pause
    exit /b 1
)

echo [4] Liberar arquivos locais (db + firmware)...
git rm --cached database\elevalocker.db 2>nul
git checkout -- firmware\elevalocker_sync\elevalocker_sync.ino 2>nul

echo [5] Reset codigo para versao nova...
git reset --hard origin/%BRANCH%
if errorlevel 1 (
    echo.
    echo RESET falhou — tentando checkout arquivo por arquivo...
    git checkout origin/%BRANCH% -- config.py app.py database.py ^
      repositories/encomenda_repository.py routes/encomendas.py ^
      services/encomenda_service.py services/notificacao_service.py ^
      services/dashboard_service.py templates/encomendas.html static/css/crud.css ^
      tools/lembretes_encomenda.py tools/lembretes_encomenda.bat tools/corrigir_conflito_git.bat
)

echo [6] Restaurar banco local (dados bancada)...
if exist "%BACKUP%\elevalocker.db.bak" (
    copy /y "%BACKUP%\elevalocker.db.bak" database\elevalocker.db >nul
    echo      Banco restaurado.
)

echo [7] Restaurar WiFi/token no firmware (do backup)...
if exist "%BACKUP%\elevalocker_sync.ino.bak" (
    for /f "tokens=*" %%a in ('findstr /c:"WIFI_SSID" /c:"WIFI_PASSWORD" /c:"SERVIDOR_URL" /c:"ESP32_TOKEN" "%BACKUP%\elevalocker_sync.ino.bak"') do echo       %%a
    echo.
    echo      Abra o .ino e confira token/WiFi se regravar ESP.
    echo      Backup: %BACKUP%\elevalocker_sync.ino.bak
)

echo.
echo ============================================================
echo   CONFERIR no painel Encomendas:
echo   - Subtitulo: prazo 3 dias ^| lembrete 24h
echo   - Filtro: Retidas (prazo expirado)
echo   - Coluna: Prazo
echo.
echo   Proximo: py app.py
echo ============================================================
pause
