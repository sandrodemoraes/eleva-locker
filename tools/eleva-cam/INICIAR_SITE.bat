@echo off
setlocal
cd /d "%~dp0..\.."

echo.
echo  ========================================
echo   ELEVA CAM — site local
echo  ========================================
echo.
echo  Site:   http://127.0.0.1:15000/eleva-cam
echo  Painel: http://127.0.0.1:15000/cameras
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
