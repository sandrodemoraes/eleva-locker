@echo off
title ELEVA LOCKER - Executar retencao LGPD Fase 4
cd /d "%~dp0"
echo ATENCAO: Rode BACKUP_DISCO_D.bat antes em producao.
where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% tools\lgpd_retencao.py --executar
pause
