@echo off
setlocal
cd /d "%~dp0"

echo.
echo  ========================================
echo   elevacam — iniciar site + tunel
echo  ========================================
echo.
echo  Vai abrir 2 janelas:
echo    1) Site  (Flask porta 15000)
echo    2) Tunel (Cloudflare)
echo.
echo  Deixe as duas abertas.
echo.

start "elevacam — Site" cmd /k "%~dp0INICIAR_SITE.bat"

echo  Aguardando o site subir...
timeout /t 4 /nobreak >nul

start "elevacam — Tunel" cmd /k "%~dp0..\..\deploy\eleva-cam\INICIAR_TUNNEL.bat"

timeout /t 3 /nobreak >nul
start "" "https://elevacam.elevalocker.com.br"

echo.
echo  Pronto. Se der erro 1033, confira a janela do Tunel.
echo.
pause
endlocal
