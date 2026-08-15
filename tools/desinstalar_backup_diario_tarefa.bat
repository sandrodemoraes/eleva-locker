@echo off
title ELEVA LOCKER - Remover backup diario agendado
cd /d "%~dp0.."

schtasks /Delete /TN "ELEVA LOCKER - Backup diario" /F 2>nul
if errorlevel 1 (
    echo Tarefa nao encontrada ou ja removida.
) else (
    echo OK — Tarefa "ELEVA LOCKER - Backup diario" removida.
)
pause
