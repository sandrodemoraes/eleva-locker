@echo off
title ELEVA LOCKER - Ligar flags LGPD Fase 2
cd /d "%~dp0"
where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% tools\ligar_lgpd_flags.py %*
pause
