@echo off
title ELEVA LOCKER - Parar Docker WhatsApp
cd /d "%~dp0.."

echo Parando container web Docker (se existir)...
docker stop elevalocker-web-1 2>nul

echo Parando Evolution API (WhatsApp)...
docker compose --profile whatsapp stop evolution-api evolution-postgres evolution-redis 2>nul

echo.
echo Pronto. O python app.py voce encerra com Ctrl+C na janela do servidor.
echo.
pause
