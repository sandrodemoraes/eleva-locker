@echo off
title ELEVA LOCKER - DIAGNOSTICO
cd /d "%~dp0"

echo Pasta: %CD%
echo.
git branch --show-current 2>nul
git rev-parse --short HEAD 2>nul
git fetch origin cursor/retirada-pacote-retido-c05c 2>nul
echo GitHub: 
git rev-parse --short origin/cursor/retirada-pacote-retido-c05c 2>nul
echo.

if exist tools\diagnostico_codigo.py (
    where py >nul 2>&1 && py tools\diagnostico_codigo.py || python tools\diagnostico_codigo.py
) else (
    echo tools\diagnostico_codigo.py NAO EXISTE — rode ATUALIZAR.bat primeiro
    echo.
    findstr /c:"Cadastre arm" templates\armarios.html 2>nul && echo OK armarios.html || echo FALTA engrenagem
    findstr /c:"confirmar_parada" app.py 2>nul && echo OK Ctrl+C || echo FALTA confirmacao Ctrl+C
    findstr /c:"/sync" routes\api\esp32_api.py 2>nul && echo OK sync ESP || echo FALTA rota sync ESP
)

echo.
pause
