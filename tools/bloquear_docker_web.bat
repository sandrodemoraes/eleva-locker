@echo off
title ELEVA LOCKER - Bloquear Docker antigo
cd /d "%~dp0.."
echo.
echo  Remove o container Docker que serve o totem ANTIGO na porta 15000.
echo  Producao usa: python app.py (via iniciar_tudo.bat)
echo.
docker update --restart=no elevalocker-web-1 2>nul
docker stop elevalocker-web-1 2>nul
docker rm -f elevalocker-web-1 2>nul
docker compose stop web 2>nul
docker compose --profile legacy-docker stop web 2>nul
echo.
echo  OK — Docker web removido.
echo  Agora rode: tools\iniciar_tudo.bat
echo.
pause
