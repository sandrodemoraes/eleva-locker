@echo off
title ELEVA LOCKER - Simular retencao LGPD Fase 4
cd /d "%~dp0"
where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% tools\lgpd_retencao.py
pause
