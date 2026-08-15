@echo off
REM Backup silencioso para Agendador de Tarefas (sem pause)
setlocal
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"
if not defined PYTHON exit /b 1

if not exist "logs" mkdir "logs"
set "LOG=logs\backup_diario.log"

echo.>> "%LOG%"
echo ==================================================>> "%LOG%"
echo BACKUP DIARIO  %date%  %time%>> "%LOG%"
echo ==================================================>> "%LOG%"

"%PYTHON%" tools\backup_obrigatorio.py>> "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"

if exist "tools\backup_firmware_esp.py" (
    echo --- firmware ESP --->> "%LOG%"
    "%PYTHON%" tools\backup_firmware_esp.py>> "%LOG%" 2>&1
)

echo FIM  exit=%RC%  %date%  %time%>> "%LOG%"
exit /b %RC%
