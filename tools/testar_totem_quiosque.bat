@echo off
title ELEVA LOCKER - Testar totem / quiosque
color 0E
cd /d "%~dp0.."

where py >nul 2>&1 && set "PY=py" || set "PY=python"

echo.
echo  Testando se o servidor responde e se /totem/quiosque existe...
echo  (Servidor precisa estar ligado: INICIAR.bat)
echo.

%PY% tools\testar_totem_quiosque.py

echo.
echo  Teste no celular (mesma WiFi):
echo    http://192.168.16.130:15000/totem/2
echo.
pause
