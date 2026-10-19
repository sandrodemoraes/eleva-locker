@echo off
setlocal EnableDelayedExpansion
title ELEVA LOCKER - Iniciar Evolution (WhatsApp)

REM ============================================================
REM  Religa o stack da Evolution API (WhatsApp) e garante o
REM  reinicio automatico. Use quando o WhatsApp der o erro
REM  "Evolution API inacessivel / WinError 10061" (container parado).
REM  Ajuste os nomes abaixo se forem diferentes (veja: docker ps -a).
REM ============================================================

set "PG=elevalocker-evolution-postgres-1"
set "REDIS=elevalocker-evolution-redis-1"
set "API=elevalocker-evolution-api-1"
set "URL=http://localhost:8080"

echo ============================================================
echo   ELEVA LOCKER - Evolution API (WhatsApp)
echo ============================================================
echo.

REM 1) Docker Desktop esta rodando?
docker info >nul 2>&1
if errorlevel 1 (
    echo ERRO: Docker Desktop nao esta rodando.
    echo Abra o Docker Desktop, espere ficar verde e rode de novo.
    pause
    exit /b 1
)

echo [1/3] Iniciando banco e cache...
docker start %PG% %REDIS% >nul 2>&1
if errorlevel 1 (
    echo AVISO: falha ao iniciar postgres/redis.
    echo        Confira os nomes com:  docker ps -a
)

echo       Aguardando 10s para o banco ficar pronto...
timeout /t 10 /nobreak >nul

echo [2/3] Iniciando Evolution API...
docker start %API% >nul 2>&1
if errorlevel 1 (
    echo AVISO: falha ao iniciar a Evolution API.
    echo        Confira os nomes com:  docker ps -a
)

REM Garante reinicio automatico apos reboot (idempotente)
docker update --restart unless-stopped %PG% %REDIS% %API% >nul 2>&1

echo [3/3] Verificando %URL% ...
timeout /t 3 /nobreak >nul
curl -s -o nul -w "       Resposta HTTP: %%{http_code}" %URL%
echo.
echo.
echo Status dos containers Evolution:
docker ps --filter "name=elevalocker-evolution" --format "  {{.Names}}  ->  {{.Status}}  {{.Ports}}"
echo.
echo Se os TRES aparecerem como "Up", o WhatsApp esta pronto.
echo Depois: no painel ELEVA, use "Reenviar" na encomenda pendente.
echo.
pause
exit /b 0
