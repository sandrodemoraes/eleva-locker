@echo off
title ELEVA LOCKER - Remover tarefa agendada
cd /d "%~dp0.."

schtasks /Delete /TN "ELEVA LOCKER - Iniciar" /F 2>nul
if errorlevel 1 (
    echo Tarefa nao encontrada ou ja removida.
) else (
    echo OK — Tarefa ELEVA LOCKER - Iniciar removida.
)
pause
