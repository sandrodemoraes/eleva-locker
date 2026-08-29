@echo off
REM Restaura tela central do armario (engrenagem): ESP, compartimentos e usuarios
cd /d C:\ElevaLocker

echo.
echo === Fetch branch ===
git fetch origin cursor/retirada-pacote-retido-c05c
if errorlevel 1 goto :erro

set BR=origin/cursor/retirada-pacote-retido-c05c

echo.
echo === Checkout arquivos da configuracao central ===
git checkout %BR% -- ^
  config.py ^
  database.py ^
  routes/armarios.py ^
  templates/armarios.html ^
  templates/armarios_detalhe.html ^
  services/armario_service.py ^
  services/esp32_portas_service.py ^
  services/esp32_service.py ^
  services/usuario_service.py ^
  repositories/armario_repository.py ^
  repositories/esp32_repository.py ^
  repositories/usuario_repository.py

if errorlevel 1 goto :erro

echo.
echo === OK! Reinicie o servidor: py app.py ===
echo     Armarios: http://192.168.16.130:15000/armarios
echo     Clique na engrenagem verde para gerenciar ESP e usuarios.
echo.
goto :fim

:erro
echo.
echo ERRO na atualizacao. Verifique git fetch e conexao.
pause
exit /b 1

:fim
pause
