@echo off
title ELEVA LOCKER - Instalar atalhos e inicio Windows
color 0A
cd /d "%~dp0.."

echo ============================================================
echo   INSTALAR ATALHOS + INICIO AUTOMATICO
echo   Pasta: %CD%
echo ============================================================
echo.
echo  Vai criar:
echo   [1] Atalho na Area de Trabalho  - ELEVA LOCKER.lnk
echo   [2] Pasta Inicializar (logon)   - ELEVA LOCKER - Iniciar.lnk
echo   [3] Tarefa agendada (apos PIN)  - atraso 45 segundos
echo.
echo  Destino: cmd /k iniciar_elevalocker.bat
echo  (NAO usa cmd.exe vazio — corrige atalho quebrado)
echo.
pause

echo.
echo [1/3] Area de Trabalho...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_desktop.ps1"
if errorlevel 1 goto :erro

echo.
echo [2/3] Iniciar com Windows (Startup)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_startup.ps1"
if errorlevel 1 goto :erro

echo.
echo [3/3] Tarefa agendada (apos login + PIN)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_inicio_automatico_tarefa.ps1"
if errorlevel 1 goto :erro

echo.
echo ============================================================
echo   PRONTO
echo ============================================================
echo.
echo  Teste: duplo clique em "ELEVA LOCKER" na Area de Trabalho
echo  Deve abrir janela CMD com py app.py
echo.
echo  Reinicie o PC para testar inicio automatico.
echo  Remover: tools\desinstalar_inicio_windows.bat
echo.
goto :fim

:erro
echo.
echo ERRO — copie a mensagem acima e envie ao suporte.
pause
exit /b 1

:fim
pause
