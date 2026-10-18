@echo off
REM Atalho na raiz — backup no disco D:
cd /d "%~dp0"
call "%~dp0tools\backup_disco_d.bat"
