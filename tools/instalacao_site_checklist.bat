@echo off
title ELEVA LOCKER - Checklist instalacao site
color 0B
cd /d "%~dp0.."

echo ============================================================
echo   CHECKLIST INSTALACAO — NOVO SITE
echo ============================================================
echo.
echo  Documento completo: docs\INSTALACAO_SITE.md
echo.
echo  RECOMENDACAO: Servidor LOCAL na mesma rede das ESPs (Opcao A)
echo.
echo  --- Rede ---
echo  [ ] Wi-Fi definido (SSID/senha)
echo  [ ] IP fixo PC servidor (ex.: 192.168.1.50)
echo  [ ] IP fixo cada ESP no roteador
echo  [ ] Firewall porta 15000 liberada
echo.
echo  --- Servidor ---
echo  [ ] C:\ElevaLocker instalado
echo  [ ] .env APP_URL_BASE = http://IP_PC:15000
echo  [ ] ESP32_MODO_SIMULACAO=0
echo  [ ] iniciar_elevalocker.bat OK
echo.
echo  --- Armario ---
echo  [ ] backup_obrigatorio.bat
echo  [ ] ESPs cadastradas + tokens no disco D
echo  [ ] configurar_bancada_24_portas (se 24 portas)
echo  [ ] diagnostico_reles_bancada --corrigir
echo.
echo  --- Firmware (cada ESP) ---
echo  [ ] WIFI_SSID / WIFI_PASSWORD
echo  [ ] SERVIDOR_URL = http://IP_PC:15000
echo  [ ] ESP32_TOKEN do cadastro
echo  [ ] RELE_ATIVO_LOW correto
echo.
echo  --- Validacao ---
echo  [ ] validar_portas_bancada --amostra
echo  [ ] totem deposito + retirada
echo  [ ] WhatsApp (se producao)
echo.
echo  Abrir documento? (S/N)
set /p ABRIR=
if /i "%ABIRIR%"=="S" start "" "docs\INSTALACAO_SITE.md"
pause
