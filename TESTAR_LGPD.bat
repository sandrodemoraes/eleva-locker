@echo off
cd /d "%~dp0"
where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% tools\testar_lgpd_fase1.py
%PY% tools\testar_lgpd_fase2.py
%PY% tools\testar_lgpd_fase3.py
%PY% tools\testar_lgpd_fase4.py
pause
