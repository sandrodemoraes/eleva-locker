@echo off
setlocal
cd /d "%~dp0..\.."

echo.
echo  ========================================
echo   elevacam — site local
echo  ========================================
echo.
echo  Local:  http://127.0.0.1:15000/eleva-cam
echo  Publico: https://elevacam.elevalocker.com.br
echo  Painel: http://127.0.0.1:15000/cameras
echo.
echo  Dica: use INICIAR_TUDO.bat para subir site + tunel juntos.
echo.

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 app.py
  goto :eof
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  python app.py
  goto :eof
)

echo [ERRO] Python nao encontrado. Instale Python 3.10+ e rode:
echo   pip install flask werkzeug
exit /b 1
