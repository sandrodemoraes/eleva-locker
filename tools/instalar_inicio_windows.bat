@echo off
title ELEVA LOCKER - Instalar atalhos (VBS)
cd /d "%~dp0.."

echo ============================================================
echo   INSTALAR ATALHOS + INICIO WINDOWS
echo   Pasta: %CD%
echo ============================================================
echo.

cscript //Nologo "%~dp0instalar_atalhos.vbs"
if errorlevel 1 (
    echo ERRO ao criar atalhos.
    pause
    exit /b 1
)

echo.
echo [Tarefa agendada] apos login + 45 segundos (PIN)...
set "BAT=%CD%\iniciar_elevalocker.bat"
schtasks /Delete /TN "ELEVA LOCKER - Iniciar" /F >nul 2>&1
schtasks /Create /TN "ELEVA LOCKER - Iniciar" /TR "cmd /k \"\"%BAT%\"\"" /SC ONLOGON /DELAY 0000:45 /F
if errorlevel 1 (
    echo AVISO: tarefa agendada falhou — atalho Startup ainda funciona apos login.
) else (
    echo OK  Tarefa ELEVA LOCKER - Iniciar criada.
)

echo.
echo ============================================================
echo   TESTE AGORA: duplo clique em ELEVA LOCKER na Area de Trabalho
echo   Log em: %CD%\logs\
echo ============================================================
echo.
pause
