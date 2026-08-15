@echo off
title ELEVA LOCKER - Instalar inicio automatico
cd /d "%~dp0.."

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "ATALHO=%STARTUP%\ELEVA LOCKER - Iniciar.lnk"

echo ============================================================
echo   Instalar inicio automatico — ELEVA LOCKER
echo ============================================================
echo.
echo Vai criar atalho na pasta Inicializar do Windows:
echo   %STARTUP%
echo.
echo Ao ligar o PC, abrira uma janela CMD com:
echo   - Docker WhatsApp (Evolution)
echo   - python app.py
echo.
echo IMPORTANTE: marque no Docker Desktop:
echo   Settings - General - Start Docker Desktop when you sign in
echo.
echo PC com PIN do Windows?
echo   Apos reiniciar o PIN bloqueia ate voce entrar.
echo   Opcao 1 — Login automatico (bancada): docs\INICIO_AUTOMATICO_PIN.md
echo   Opcao 2 — Tarefa apos login: tools\instalar_inicio_automatico_tarefa.bat
echo.
pause

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_startup.ps1"
if errorlevel 1 (
    echo.
    echo ERRO ao criar atalho.
    goto fim
)

if exist "%ATALHO%" (
    echo.
    echo OK — Atalho criado!
    echo Reinicie o PC para testar.
    echo.
    echo Para remover: tools\desinstalar_inicio_automatico.bat
) else (
    echo.
    echo ERRO ao criar atalho.
)

:fim
echo.
pause
