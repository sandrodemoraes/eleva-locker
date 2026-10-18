@echo off
title ELEVA LOCKER - Reset branch retida (CUIDADO)
color 0C
cd /d "%~dp0.."

set "BRANCH=cursor/retirada-pacote-retido-c05c"

echo ============================================================
echo   RESET TOTAL para origin/%BRANCH%
echo ============================================================
echo.
echo  Isso DESCARTA alteracoes locais no codigo (nao mexe no .env).
echo  Use se corrigir_conflito_git.bat nao resolver.
echo.
set /p OK="Digite SIM para continuar: "
if /i not "%OK%"=="SIM" exit /b 0

git merge --abort 2>nul
git fetch origin %BRANCH%
git reset --hard origin/%BRANCH%

echo.
echo Feito. Rode: py app.py
pause
