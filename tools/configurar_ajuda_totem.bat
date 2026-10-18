@echo off
title ELEVA LOCKER - Configurar ajuda totem (WhatsApp portaria)
color 0B
cd /d "%~dp0.."

where py >nul 2>&1 && set "PY=py" || set "PY=python"

echo.
echo  Configure o WhatsApp da PORTARIA para avisos do totem.
echo  Exemplo: 48999998888 (DDD + numero, sem espacos)
echo.

%PY% tools\configurar_ajuda_totem.py

echo.
pause
