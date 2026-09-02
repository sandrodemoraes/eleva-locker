@echo off
title ELEVA LOCKER - Diagnostico de atualizacao
cd /d "%~dp0.."

echo.
echo === Git ===
git branch --show-current
git rev-parse --short HEAD 2>nul
git fetch origin cursor/retirada-pacote-retido-c05c 2>nul
echo Remoto:
git rev-parse --short origin/cursor/retirada-pacote-retido-c05c 2>nul
echo.
git status -sb
echo.

echo === Arquivos (engrenagem / Ctrl+C) ===
findstr /c:"Cadastre arm" templates\armarios.html 2>nul && echo   OK armarios.html || echo   FALTA engrenagem em armarios.html
if exist templates\armarios_detalhe.html (echo   OK armarios_detalhe.html) else (echo   FALTA armarios_detalhe.html)
findstr /c:"Encerrar o servidor ELEVA LOCKER" app.py 2>nul && echo   OK confirmacao Ctrl+C || echo   FALTA confirmacao Ctrl+C
echo.

where py >nul 2>&1 && set "PY=py" || set "PY=python"
%PY% tools\diagnostico_codigo.py

echo.
echo Se FALTA algo: tools\atualizar_bancada.bat
echo.
pause
