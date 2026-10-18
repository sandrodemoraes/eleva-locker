@echo off
title ELEVA LOCKER - Modo quiosque (celular)
color 0B
cd /d "%~dp0.."

set "URL=http://192.168.16.130:15000/totem/2?kiosk=1"
set "URL_CURTA=http://192.168.16.130:15000/totem/quiosque"
set "URL_JSON=http://192.168.16.130:15000/totem/quiosque/fully.json"

for /f "delims=" %%U in ('python "%~dp0url_totem_quiosque.py" 2^>nul') do (
    set "URL=%%U"
    goto :urls_ok
)
:urls_ok
for /f "skip=1 delims=" %%U in ('python "%~dp0url_totem_quiosque.py" 2^>nul') do (
    set "URL_CURTA=%%U"
    goto :url_curta_ok
)
:url_curta_ok
for /f "skip=2 delims=" %%U in ('python "%~dp0url_totem_quiosque.py" 2^>nul') do (
    set "URL_JSON=%%U"
    goto :url_json_ok
)
:url_json_ok

echo ============================================================
echo   MODO QUIOSQUE — Celular como Totem (armario ID 2)
echo ============================================================
echo.
echo  URL do totem (modo quiosque):
echo    %URL%
echo.
echo  Se der "pagina nao encontrada", use esta (sempre funciona):
echo    http://192.168.16.130:15000/totem/2
echo.
echo  Na bancada: ATUALIZAR.bat ^> reinicie INICIAR.bat ^> TESTAR_TOTEM.bat
echo.
echo  Atalho curto:
echo    %URL_CURTA%
echo.
echo  Arquivo de config Fully Kiosk (importar no celular):
echo    %URL_JSON%
echo.
echo  REQUISITO: celular na mesma WiFi da bancada (192.168.16.x)
echo  Servidor ELEVA LOCKER ligado (INICIAR.bat)
echo.
echo ============================================================
echo  PASSO A PASSO — Android com Fully Kiosk Browser
echo ============================================================
echo.
echo  1. Instale "Fully Kiosk Browser" na Play Store (gratis)
echo.
echo  2. Abra o app ^> Menu ^> Configuracoes ^> Web Content Settings
echo     Start URL = %URL%
echo.
echo  3. Configuracoes ^> Kiosk Mode (Modo quiosque)
echo     - Ativar Modo quiosque = SIM
echo     - Launch on Boot = SIM (abre ao ligar celular)
echo     - Keep Screen On = SIM
echo     - Disable Home Button = SIM
echo.
echo  4. Configuracoes ^> Other Settings ^> Import Settings
echo     Baixe no celular: %URL_JSON%
echo     (ou copie o link no Chrome e importe no Fully)
echo.
echo  5. Conceda "Administrador do dispositivo" quando pedir
echo     (bloqueia botao Home e impede sair do totem)
echo.
echo  6. Deixe carregando na tomada. Ajustes ^> Tela ^> Nunca desligar
echo.
echo  SAIR DO QUIOSQUE (manutencao):
echo  Toque 7x no canto superior direito ^> digite PIN do Fully
echo  (PIN padrao: definido na 1a vez que abrir o app)
echo.
echo ============================================================
echo.
set /p ABRIR=Abrir totem quiosque no PC para testar? (S/N): 
if /i "%ABRIR%"=="S" start "" "%URL%"
echo.
pause
