@echo off
title ELEVA LOCKER - Atualizar bancada (forcado)
color 0A
cd /d "%~dp0.."

set "BRANCH=cursor/retirada-pacote-retido-c05c"
set "BACKUP=D:\ElevaLockerBackup\git_update"

echo ============================================================
echo   ATUALIZAR BANCADA — %BRANCH%
echo   Preserva: database\elevalocker.db e .env
echo ============================================================
echo.
echo  1. Pare o servidor antes (Ctrl+C na janela do py app.py)
echo  2. Este script faz reset --hard no CODIGO (nao apaga o banco)
echo.
pause

if not exist "%BACKUP%" mkdir "%BACKUP%"
if exist database\elevalocker.db (
    copy /y database\elevalocker.db "%BACKUP%\elevalocker.db.bak" >nul
    echo Backup banco: %BACKUP%\elevalocker.db.bak
)

echo.
echo [1/6] Abortar merge pendente...
git merge --abort 2>nul

echo [2/6] Buscar GitHub...
git fetch origin %BRANCH%
if errorlevel 1 (
    echo ERRO: git fetch falhou. Internet ou git instalado?
    pause
    exit /b 1
)

echo [3/6] Trocar para branch correta...
git checkout %BRANCH% 2>nul
if errorlevel 1 (
    git checkout -b %BRANCH% origin/%BRANCH%
)

echo [4/6] Reset codigo = igual ao GitHub...
git rm --cached database\elevalocker.db 2>nul
git reset --hard origin/%BRANCH%
if errorlevel 1 (
    echo ERRO no reset.
    pause
    exit /b 1
)

echo [5/6] Restaurar banco local...
if exist "%BACKUP%\elevalocker.db.bak" (
    copy /y "%BACKUP%\elevalocker.db.bak" database\elevalocker.db >nul
    echo Banco restaurado.
)

echo [6/6] Matriz + diagnostico...
where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% tools\recriar_matriz_armario.py
%PY% tools\diagnostico_codigo.py

echo.
echo ============================================================
echo   PROXIMO PASSO (obrigatorio):
echo     py app.py
echo.
echo   No navegador: Ctrl+F5 em http://192.168.16.130:15000/armarios
echo   Deve aparecer coluna Portas + engrenagem verde
echo ============================================================
pause
