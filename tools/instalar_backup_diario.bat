@echo off
title ELEVA LOCKER - Agendar backup diario (D:)
cd /d "%~dp0.."

set "TAREFA=ELEVA Locker Backup Disco D"
set "SCRIPT=%~dp0backup_disco_d.bat"
set "HORA=03:00"

echo ============================================================
echo   Agendar backup diario as %HORA%
echo ============================================================
echo.
echo Tarefa: %TAREFA%
echo Script: %SCRIPT%
echo.
echo Requer CMD como Administrador.
echo.
pause

schtasks /Create /TN "%TAREFA%" /TR "\"%SCRIPT%\"" /SC DAILY /ST %HORA% /RL HIGHEST /F

if errorlevel 1 (
    echo.
    echo ERRO ao criar tarefa. Execute como Administrador.
) else (
    echo.
    echo OK — Backup agendado todo dia as %HORA%
    echo Teste agora: tools\backup_disco_d.bat
    echo.
    echo Remover: schtasks /Delete /TN "%TAREFA%" /F
)

echo.
pause
