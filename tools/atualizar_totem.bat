@echo off
REM Atualiza TODOS os arquivos do totem v2.4.8 (evita ModuleNotFoundError)
cd /d C:\ElevaLocker

echo.
echo === Fetch branch ===
git fetch origin cursor/retirada-pacote-retido-c05c
if errorlevel 1 goto :erro

set BR=origin/cursor/retirada-pacote-retido-c05c

echo.
echo === Checkout arquivos do totem ===
git checkout %BR% -- ^
  config.py ^
  database.py ^
  esp32.py ^
  routes/totem.py ^
  middleware/rate_limit.py ^
  middleware/operador_scope.py ^
  services/totem_auth_service.py ^
  services/totem_destinatario_service.py ^
  services/totem_ajuda_service.py ^
  services/esp32_sync_service.py ^
  services/encomenda_service.py ^
  services/esp32_service.py ^
  services/notificacao_service.py ^
  services/armario_service.py ^
  repositories/encomenda_repository.py ^
  repositories/compartimento_repository.py ^
  repositories/notificacao_repository.py ^
  repositories/totem_ajuda_repository.py ^
  repositories/armario_repository.py ^
  templates/totem.html ^
  static/css/totem.css ^
  static/css/eleva-theme.css ^
  static/brand/logo-eleva-locker-icon.svg ^
  tools/corrigir_totem_armario.py ^
  tools/corrigir_totem_armario.bat

if errorlevel 1 goto :erro

echo.
echo === Corrigir armario e .env ===
py tools\corrigir_totem_armario.py
if errorlevel 1 goto :erro

echo.
echo === OK! Inicie o servidor: py app.py ===
echo     Totem: http://192.168.16.130:15000/totem/2
echo.
goto :fim

:erro
echo.
echo ERRO na atualizacao. Verifique git fetch e conexao.
pause
exit /b 1

:fim
pause
