@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo  ========================================
echo   elevacam — Cloudflare Tunnel
echo  ========================================
echo.
echo  URLs:
echo    https://elevacam.elevalocker.com.br
echo    https://elevalocker.com.br
echo  Origem: http://127.0.0.1:15000
echo.
echo  Deixe o Flask (INICIAR_SITE.bat) rodando.
echo  Ou use tools\eleva-cam\INICIAR_TUDO.bat
echo.

set "CF="
if exist "%~dp0cloudflared.exe" set "CF=%~dp0cloudflared.exe"
if not defined CF if exist "%USERPROFILE%\Downloads\cloudflared.exe" set "CF=%USERPROFILE%\Downloads\cloudflared.exe"
if not defined CF if exist "%USERPROFILE%\cloudflared.exe" set "CF=%USERPROFILE%\cloudflared.exe"
if not defined CF (
  where cloudflared.exe >nul 2>&1 && for /f "delims=" %%I in ('where cloudflared.exe') do set "CF=%%I" & goto :have_cf
)
goto :check_cf

:have_cf
:check_cf
if not defined CF (
  echo [ERRO] cloudflared.exe nao encontrado.
  echo.
  echo Procure no PC e copie para esta pasta:
  echo   %cd%
  echo.
  echo Download:
  echo   https://github.com/cloudflare/cloudflared/releases
  echo Arquivo Windows amd64 - renomeie para cloudflared.exe
  echo.
  echo Ou no PowerShell:
  echo   Get-ChildItem C:\Users\terminal -Filter cloudflared.exe -Recurse -ErrorAction SilentlyContinue
  exit /b 1
)

if not exist "config.tunnel.yml" (
  echo [ERRO] Crie config.tunnel.yml a partir de config.tunnel.example.yml
  echo   copy config.tunnel.example.yml config.tunnel.yml
  exit /b 1
)

echo  Usando: %CF%
echo.
"%CF%" tunnel --config "%~dp0config.tunnel.yml" run
endlocal
