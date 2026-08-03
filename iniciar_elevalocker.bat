@echo off
title ELEVA LOCKER
color 0A
cd /d "%~dp0"

set "MODO_STARTUP=0"
if /I "%~1"=="/startup" set "MODO_STARTUP=1"

echo ============================================================
echo                    ELEVA LOCKER
echo ============================================================
echo.
echo Iniciando sistema na porta 15000...
echo URL: http://localhost:15000
echo.
echo Nao feche esta janela enquanto o sistema estiver em uso.
if "%MODO_STARTUP%"=="1" echo Modo: inicio automatico com o Windows
echo ============================================================
echo.

:: No atalho manual, abre o navegador. No boot automatico, nao abre.
if "%MODO_STARTUP%"=="0" (
    start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:15000"
)

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
if "%MODO_STARTUP%"=="0" pause
exit /b 1

:fim
echo.
echo Sistema encerrado.
if "%MODO_STARTUP%"=="0" pause
