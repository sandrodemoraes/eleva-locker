@echo off
title ELEVA LOCKER - Configurar celular Totem Matriz
color 0B
cd /d "%~dp0.."

set "URL=http://192.168.16.130:15000/totem/2"
set "URL_CURTA=http://192.168.16.130:15000/totem/matriz"

echo ============================================================
echo   CELULAR COMO TOTEM — Armario ID 2 (Matriz)
echo ============================================================
echo.
echo  URL fixa (use no celular):
echo    %URL%
echo.
echo  Atalho curto:
echo    %URL_CURTA%
echo.
echo  REQUISITO: celular na mesma WiFi da bancada (192.168.16.x)
echo.
echo ------------------------------------------------------------
echo  ANDROID (Chrome)
echo ------------------------------------------------------------
echo  1. Abra a URL acima no Chrome
echo  2. Menu (3 pontos) - "Adicionar a tela inicial"
echo  3. Nome: Totem Matriz
echo  4. Abra pelo icone na tela inicial (modo app)
echo.
echo  Para NAO desligar a tela:
echo  Ajustes - Tela - Tempo de espera = 30 min (ou Nunca)
echo  Deixe carregando na tomada.
echo.
echo ------------------------------------------------------------
echo  IPHONE (Safari)
echo ------------------------------------------------------------
echo  1. Abra a URL no Safari (nao Chrome)
echo  2. Compartilhar - "Adicionar a Tela de Inicio"
echo  3. Nome: Totem Matriz
echo.
echo ------------------------------------------------------------
echo  MODO QUIOSQUE (celular so abre o totem)
echo ------------------------------------------------------------
echo  Rode: CONFIGURAR_QUIOSQUE.bat
echo  App: Fully Kiosk Browser (Play Store)
echo.
echo ============================================================
echo.
set /p ABRIR=Abrir totem no PC agora para testar? (S/N): 
if /i "%ABRIR%"=="S" start "" "%URL%"
echo.
pause
