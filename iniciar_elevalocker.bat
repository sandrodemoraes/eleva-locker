@echo off
title ELEVA LOCKER
color 0A
cd /d "%~dp0"

echo ============================================================
echo                    ELEVA LOCKER
echo ============================================================
echo.
echo Iniciando sistema na porta 15000...
echo URL: http://localhost:15000
echo.
echo Nao feche esta janela enquanto o sistema estiver em uso.
echo ============================================================
echo.

:: Abre o navegador apos alguns segundos
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:15000"

:: Tenta py (launcher do Windows), depois python
where py >nul 2>&1
if %errorlevel%==0 (
    py app.py
    goto :fim
)

where python >nul 2>&1
if %errorlevel%==0 (
    python app.py
    goto :fim
)

echo.
echo ERRO: Python nao encontrado no PATH.
echo Instale o Python e marque a opcao "Add Python to PATH".
echo.
pause
exit /b 1

:fim
echo.
echo Sistema encerrado.
pause
