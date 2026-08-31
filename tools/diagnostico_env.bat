@echo off
cd /d "%~dp0.."
where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% tools\diagnostico_env.py
pause
