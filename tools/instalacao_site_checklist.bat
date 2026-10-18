@echo off
title ELEVA LOCKER - Checklist instalacao site
color 0B
cd /d "%~dp0.."

echo ============================================================
echo   CHECKLIST INSTALACAO — SITE PILOTO (Modelo A)
echo ============================================================
echo.
echo  Documento completo: docs\INSTALACAO_SITE.md
echo  WireGuard peers:   docs\WIREGUARD_PEERS.md
echo.
echo  MODELO A = PC local no site — ESP apontam IP LOCAL
echo  WireGuard = so gestao Matriz (depois do piloto local OK)
echo.
echo  --- Criar site ---
echo  [ ] INSTALAR_SITE.bat ou bootstrap_site_piloto.py
echo  [ ] Sites\<codigo>\env.txt copiado para .env
echo.
echo  --- Rede local ---
echo  [ ] IP fixo PC servidor
echo  [ ] IP fixo cada ESP
echo  [ ] Firewall porta 15000 (rede privada)
echo  [ ] Totem na mesma Wi-Fi
echo.
echo  --- Servidor ---
echo  [ ] APP_URL_BASE = http://IP_LOCAL:15000
echo  [ ] ESP32_MODO_SIMULACAO=0
echo  [ ] INICIAR.bat OK
echo.
echo  --- Firmware ---
echo  [ ] SERVIDOR_URL = IP LOCAL (nao Matriz)
echo  [ ] ESP32_TOKEN do cadastro
echo  [ ] Sync OK no Serial Monitor
echo.
echo  --- Validacao ---
echo  [ ] ESP online no painel
echo  [ ] Totem deposito + retirada
echo  [ ] Teste OFFLINE: desligar internet, LAN continua
echo.
echo  --- WireGuard (fase 2) ---
echo  [ ] Peer cadastrado no HUB Matriz
echo  [ ] Matriz acessa http://10.255.0.NN:15000
echo  [ ] GET /api/v1/status com API key
echo.
echo  Abrir documento? (S/N)
set /p ABRIR=
if /i "%ABRIR%"=="S" start "" "docs\INSTALACAO_SITE.md"
pause
