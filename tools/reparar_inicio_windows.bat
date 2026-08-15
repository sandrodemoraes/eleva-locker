@echo off
title ELEVA LOCKER - Reparar Inicio Windows
color 0A
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"

echo ============================================================
echo   REPARAR INICIO DO WINDOWS — verde + armarios
echo ============================================================
echo.
echo  Pasta oficial: C:\ElevaLocker
echo  Problema comum: atalho aponta para pasta/branch errada
echo                  ou navegador abre IP publico (azul / 0 armarios)
echo.

if /i not "%CD%"=="C:\ElevaLocker" (
    echo  AVISO: voce esta em %CD%
    echo  O ideal e rodar isto em C:\ElevaLocker
    echo.
)

echo [1] Preparar bancada SQLite + site_id + ELEVA_PAINEL_URL...
%PYTHON% tools\preparar_inicio_bancada.py

echo.
echo [1b] Parar Docker web antigo (tela azul na porta 15000)...
docker stop elevalocker-web-1 2>nul
docker rm -f elevalocker-web-1 2>nul
echo [2] Recriar atalho Iniciar do Windows...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_startup.ps1"

echo.
echo [3] Recriar atalho Area de Trabalho...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_desktop.ps1"

echo.
echo [4] Atualizar tarefa agendada (apos PIN)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_inicio_automatico_tarefa.ps1"

echo.
echo [5] Conferir atalhos (Startup vs Desktop)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0diagnosticar_inicio_windows.ps1"

echo.
echo ============================================================
echo   PRONTO
echo ============================================================
echo.
echo  Reinicie o PC ou rode: C:\ElevaLocker\iniciar_elevalocker.bat
echo.
echo  Abra SEMPRE: http://192.168.16.130:15000/dashboard
echo  (nao use IP publico 177.x no navegador da bancada)
echo  No painel use filtro: Todos os sites (topo)
echo  Deve abrir VERDE com armarios
echo.
pause
