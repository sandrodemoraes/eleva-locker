@echo off
title ELEVA LOCKER - Parar servicos
cd /d "%~dp0.."

echo Parando servidor web (python + Docker web)...
call "%~dp0parar_servidor.bat" nopause

echo.
echo Parando Evolution API (WhatsApp)...
docker compose --profile whatsapp stop evolution-api evolution-postgres evolution-redis 2>nul

echo.
echo Tudo parado.
pause
