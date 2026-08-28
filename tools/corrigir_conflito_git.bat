@echo off
title ELEVA LOCKER - Corrigir conflito Git
color 0C
cd /d "%~dp0.."

echo ============================================================
echo   CORRIGIR database.py (marcadores de conflito Git)
echo ============================================================
echo.
echo  Erro tipico: SyntaxError linha com ^>^>^>^>^>^>^>
echo.

findstr /s /m /r "<<<<<<< ======= >>>>>>>" *.py 2>nul
if errorlevel 1 (
    echo Nenhum conflito encontrado em .py na raiz.
) else (
    echo ARQUIVOS COM CONFLITO listados acima.
)

echo.
echo Restaurando database.py da branch retida-pacote-retido...
git fetch origin cursor/retirada-pacote-retido-c05c 2>nul
git checkout origin/cursor/retirada-pacote-retido-c05c -- database.py 2>nul
if errorlevel 1 (
    echo AVISO: checkout falhou — tente manualmente no VS Code.
) else (
    echo database.py restaurado.
)

echo.
echo Proximo: py app.py
echo.
pause
