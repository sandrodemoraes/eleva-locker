@echo off
title ELEVA LOCKER - ATUALIZAR
color 0A
cd /d "%~dp0"

set "BRANCH=cursor/retirada-pacote-retido-c05c"
set "BACKUP=D:\ElevaLockerBackup\git_update"

echo ============================================================
echo   ATUALIZAR ELEVA LOCKER
echo   Branch: %BRANCH%
echo   Pasta:  %CD%
echo ============================================================
echo.
echo  Pare o servidor antes (Ctrl+C na janela do py app.py)
echo.
pause

where git >nul 2>&1
if errorlevel 1 (
    echo ERRO: Git nao encontrado. Instale Git for Windows.
    pause
    exit /b 1
)

if not exist database\elevalocker.db (
    echo AVISO: banco database\elevalocker.db nao encontrado nesta pasta.
) else (
    if not exist "%BACKUP%" mkdir "%BACKUP%"
    copy /y database\elevalocker.db "%BACKUP%\elevalocker.db.bak" >nul
    echo Backup banco: %BACKUP%\elevalocker.db.bak
)

echo.
echo [1] git fetch...
git fetch origin %BRANCH%
if errorlevel 1 (
    echo ERRO no fetch. Verifique internet.
    pause
    exit /b 1
)

echo [2] git checkout branch...
git checkout %BRANCH% 2>nul
if errorlevel 1 git checkout -b %BRANCH% origin/%BRANCH%

echo [3] git reset --hard (codigo = GitHub)...
git rm --cached database\elevalocker.db 2>nul
git reset --hard origin/%BRANCH%
if errorlevel 1 (
    echo ERRO no reset.
    pause
    exit /b 1
)

if exist "%BACKUP%\elevalocker.db.bak" (
    copy /y "%BACKUP%\elevalocker.db.bak" database\elevalocker.db >nul
    echo Banco local restaurado.
)

where py >nul 2>&1 && set "PY=py" || set "PY=python"
if exist tools\recriar_matriz_armario.py %PY% tools\recriar_matriz_armario.py
if exist tools\diagnostico_codigo.py (
    %PY% tools\diagnostico_codigo.py
) else (
    findstr /c:"Cadastre arm" templates\armarios.html 2>nul && echo OK engrenagem || echo FALTA engrenagem - git reset falhou?
)

echo.
echo ============================================================
echo   Pronto. Inicie:
echo     INICIAR ELEVA LOCKER.bat
echo   ou: py app.py
echo.
echo   No navegador: Ctrl+F5 em /armarios
echo ============================================================
pause
