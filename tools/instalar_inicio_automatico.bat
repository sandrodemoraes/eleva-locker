@echo off
title ELEVA LOCKER - Instalar inicio automatico
cd /d "%~dp0.."

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "ATALHO=%STARTUP%\ELEVA LOCKER - Iniciar.lnk"
set "BAT=%~dp0iniciar_tudo.bat"

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
echo   Settings ^> General ^> Start Docker Desktop when you sign in
echo.
pause

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $s = $ws.CreateShortcut('%ATALHO%'); ^
   $s.TargetPath = '%BAT%'; ^
   $s.WorkingDirectory = '%~dp0..'; ^
   $s.WindowStyle = 1; ^
   $s.Description = 'ELEVA LOCKER - Docker WhatsApp + app.py'; ^
   $s.Save()"

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

echo.
pause
