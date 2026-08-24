@echo off
title ELEVA LOCKER - Inicio automatico (Agendador de Tarefas)
color 0B
cd /d "%~dp0.."

echo ============================================================
echo   INICIO AUTOMATICO — Agendador de Tarefas
echo ============================================================
echo.
echo  Para PC com PIN do Windows:
echo  - Apos REINICIAR, voce digita PIN UMA vez
echo  - Em ~45 segundos o ELEVA LOCKER sobe sozinho
echo.
echo  Para subir SEM digitar PIN (PC so da bancada):
echo  - Leia docs\INICIO_AUTOMATICO_PIN.md (login automatico netplwiz)
echo.
pause

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_inicio_automatico_tarefa.ps1"
if errorlevel 1 (
    echo ERRO ao criar tarefa.
    pause
    exit /b 1
)

echo.
echo Tambem pode manter o atalho na pasta Inicializar:
echo   tools\instalar_inicio_automatico.bat
echo.
pause
