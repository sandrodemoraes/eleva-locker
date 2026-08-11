@echo off
REM Abre URL no navegador padrao apos 6 segundos (uso interno iniciar_tudo.bat)
timeout /t 6 /nobreak >nul
start "" "%~1"
