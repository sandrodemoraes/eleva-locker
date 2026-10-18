@echo off
title ELEVA LOCKER - Teste LGPD Fase 1
cd /d "%~dp0.."
where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% tools\testar_lgpd_fase1.py
pause
