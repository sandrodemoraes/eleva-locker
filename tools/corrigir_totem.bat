@echo off
title ELEVA LOCKER - Corrigir totem v2
color 0E
cd /d "%~dp0.."

set "BRANCH=cursor/totem-seguro-c05c"
set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"

echo.
echo  ============================================================
echo   CORRIGIR TOTEM v2 — ELEVA LOCKER
echo  ============================================================
echo   Pasta: %CD%
echo   Branch: %BRANCH%
echo  ============================================================
echo.

echo [1] Parando e REMOVENDO Docker web (versao antiga)...
docker stop elevalocker-web-1 2>nul
docker rm -f elevalocker-web-1 2>nul
docker compose stop web 2>nul
docker compose --profile legacy-docker stop web 2>nul

echo [2] Liberando porta 15000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":15000" ^| findstr "LISTENING"') do (
    echo     Encerrando PID %%a
    taskkill /F /PID %%a 2>nul
)

echo [3] Git — baixando totem v2...
git fetch origin %BRANCH%
if errorlevel 1 (
    echo ERRO: git fetch falhou. Verifique internet e Git.
    goto fim
)
git checkout %BRANCH%
if errorlevel 1 (
    echo ERRO: git checkout falhou.
    goto fim
)
git pull origin %BRANCH%
if errorlevel 1 (
    echo ERRO: git pull falhou.
    goto fim
)
git log -1 --oneline

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    goto fim
)

echo [4] Verificando arquivos...
%PYTHON% tools\verificar_totem.py

echo [5] Abrindo servidor em nova janela...
start "ELEVA LOCKER" cmd /k "cd /d %CD% && tools\iniciar_tudo.bat"

echo.
echo  ============================================================
echo   AGUARDE 30s e teste:
echo   http://192.168.16.130:15000/totem/versao
echo   Deve mostrar: "ok": true, "versao": "2.3.4"
echo.
echo   Totem: http://192.168.16.130:15000/totem/3  (Ctrl+F5)
echo  ============================================================
echo.

:fim
pause
