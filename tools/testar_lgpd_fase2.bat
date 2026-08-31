@echo off
title ELEVA LOCKER - Teste LGPD Fase 2
cd /d "%~dp0.."
where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% tools\testar_lgpd_fase2.py
pause
