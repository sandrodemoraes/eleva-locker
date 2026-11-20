@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "LOG=%~dp0..\..\logs\elevacam-autoinicio.log"
if not exist "%~dp0..\..\logs" mkdir "%~dp0..\..\logs"

echo ===== %DATE% %TIME% — autoinicio elevacam =====>> "%LOG%"

echo.
echo  elevacam — inicio automatico apos ligar o PC
echo  Aguardando a rede...
echo.

REM Espera ate 3 minutos pela internet (energia / modem / Wi-Fi)
set /a TENTATIVAS=0
:espera_rede
set /a TENTATIVAS+=1
ping -n 1 -w 2000 1.1.1.1 >nul 2>&1
if %ERRORLEVEL%==0 goto rede_ok
ping -n 1 -w 2000 8.8.8.8 >nul 2>&1
if %ERRORLEVEL%==0 goto rede_ok
if %TENTATIVAS% GEQ 36 (
  echo  [AVISO] Rede demorou. Seguindo mesmo assim...>> "%LOG%"
  echo  [AVISO] Rede demorou. Seguindo mesmo assim...
  goto sobe
)
timeout /t 5 /nobreak >nul
goto espera_rede

:rede_ok
echo  Rede OK. Subindo site + tunel...
echo  Rede OK>> "%LOG%"

:sobe
REM Pequena folga extra para DNS / Cloudflare
timeout /t 10 /nobreak >nul

start "elevacam — Site" cmd /k "%~dp0INICIAR_SITE.bat"
timeout /t 6 /nobreak >nul
start "elevacam — Tunel" cmd /k "%~dp0..\..\deploy\eleva-cam\INICIAR_TUNNEL.bat"

echo  Site e tunel iniciados. Deixe as janelas abertas.
echo  Iniciados OK>> "%LOG%"
endlocal
exit /b 0
