@echo off
setlocal
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

if not exist "cloudflared.exe" (
  echo [ERRO] cloudflared.exe nao encontrado nesta pasta.
  echo Baixe em:
  echo   https://github.com/cloudflare/cloudflared/releases
  echo Renomeie para cloudflared.exe e copie para:
  echo   %cd%
  exit /b 1
)

if not exist "config.tunnel.yml" (
  echo [ERRO] Crie config.tunnel.yml a partir de config.tunnel.example.yml
  echo   copy config.tunnel.example.yml config.tunnel.yml
  exit /b 1
)

cloudflared.exe tunnel --config config.tunnel.yml run
endlocal
