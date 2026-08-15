@echo off
title ELEVA LOCKER - Backup diario 11h (Agendador)
color 0E
cd /d "%~dp0.."

echo ============================================================
echo   BACKUP DIARIO — Agendador de Tarefas Windows
echo ============================================================
echo.
echo  Cria tarefa: todo dia as 11:00
echo  Faz: banco + .env + disco D: (+ firmware ESP se existir)
echo  Log: logs\backup_diario.log
echo.
echo  IMPORTANTE: clique com botao direito neste arquivo
echo  e escolha "Executar como administrador" se der erro de permissao.
echo.
pause

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_backup_diario_tarefa.ps1" -Hora "11:00"
if errorlevel 1 (
    echo.
    echo ERRO ao criar tarefa. Tente "Executar como administrador".
    pause
    exit /b 1
)

echo.
echo Deseja rodar um backup de teste agora? (S/N)
choice /C SN /N /M "Teste: "
if errorlevel 2 goto fim
call tools\backup_diario.bat
echo.
echo Veja o resultado em logs\backup_diario.log
:fim
pause
