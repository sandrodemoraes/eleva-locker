@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo  ========================================
echo   elevacam — instalar inicio automatico
echo  ========================================
echo.
echo  Isso cria um atalho na pasta Inicializar
echo  do Windows. Ao ligar o PC e entrar no
echo  Windows, o site + tunel sobem sozinhos.
echo.

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "ALVO=%~dp0INICIAR_AUTOMATICO.bat"
set "ATALHO=%STARTUP%\elevacam-autoinicio.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%ATALHO%');" ^
  "$s.TargetPath = '%ALVO%';" ^
  "$s.WorkingDirectory = '%~dp0';" ^
  "$s.WindowStyle = 1;" ^
  "$s.Description = 'elevacam site + Cloudflare Tunnel';" ^
  "$s.Save()"

if exist "%ATALHO%" (
  echo  OK: atalho criado em
  echo  %ATALHO%
  echo.
  echo  Proximo passo IMPORTANTE — BIOS:
  echo   apos queda de energia, o PC deve ligar sozinho.
  echo   Veja docs\ELEVA_CAM_AUTOINICIO.md
  echo.
) else (
  echo  [ERRO] Nao foi possivel criar o atalho.
  echo  Crie manualmente: Win+R -^> shell:startup
  echo  e arraste um atalho de INICIAR_AUTOMATICO.bat
)

echo.
pause
endlocal
