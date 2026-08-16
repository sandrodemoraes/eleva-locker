@echo off
title ELEVA LOCKER - Recuperar totem (404 = servidor antigo)
color 0E
cd /d "%~dp0.."

set "BRANCH=cursor/totem-seguro-c05c"
set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"

echo.
echo  ============================================================
echo   RECUPERAR TOTEM v2
echo  ============================================================
echo.
echo  Se /totem/versao da 404, a porta 15000 esta com servidor ANTIGO
echo  (container Docker ou app.py desatualizado).
echo.
echo  Este script: git pull + mata Docker + sobe python app.py NOVO
echo  ============================================================
echo.

if not defined PYTHON (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo [1] Atualizando codigo (%BRANCH%)...
git fetch origin %BRANCH%
git checkout %BRANCH% 2>nul
git pull origin %BRANCH%
if errorlevel 1 (
    echo ERRO: git pull falhou.
    pause
    exit /b 1
)
git log -1 --oneline
echo.

echo [2] Verificando arquivos no disco...
%PYTHON% tools\verificar_totem.py
echo.

echo [3] Parando servidor antigo...
%PYTHON% tools\parar_servidor.py
echo.

echo [4] Subindo servidor NOVO — mantenha a janela aberta!
echo     Teste: http://localhost:15000/totem/versao
echo     Deve mostrar JSON com "ok": true
echo.
start "" "http://localhost:15000/totem/versao"
%PYTHON% app.py

pause
