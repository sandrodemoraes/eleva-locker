@echo off
title ELEVA LOCKER - Verificar dominio publico
cd /d "C:\ElevaLocker"
where py >nul 2>&1 && set "PY=py" || set "PY=python"
echo.
echo === Diagnostico .env ===
%PY% tools\diagnostico_env.py
echo.
echo === Verificar dominio (DNS + HTTPS) ===
%PY% tools\verificar_dominio_publico.py
echo.
echo Passo a passo completo: docs\DOMINIO_PUBLICO_PASSO_A_PASSO.md
pause
