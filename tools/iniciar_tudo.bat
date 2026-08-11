@echo off
title ELEVA LOCKER - Iniciar servicos
color 0B
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"

if not defined PYTHON (
    echo ERRO: Python nao encontrado no PATH.
    pause
    exit /b 1
)

REM Bancada: SQLite obrigatorio em TODA a sessao (nao so no app.py)
set ELEVA_BANCADA=1
set DATABASE_URL=

echo Usando: %PYTHON%
echo Pasta:   %CD%
echo.

echo [1/3] Garantindo .env bancada (SQLite)...
%PYTHON% -c "import sys; sys.path.insert(0,'.'); from tools.env_bancada import garantir_bancada_env; garantir_bancada_env()"
if errorlevel 1 (
    echo AVISO: nao foi possivel ajustar .env — verifique C:\ElevaLocker\.env
)

echo [2/3] Parando servidor antigo (porta 15000)...
%PYTHON% tools\parar_servidor.py nopause 2>nul

echo [3/3] Docker WhatsApp + servidor...
%PYTHON% tools\iniciar_tudo.py
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Servidor ELEVA LOCKER — porta 15000
echo   Mantenha ESTA janela aberta
echo   Ctrl+C para parar o servidor
echo ============================================================
echo.

REM URL do painel (.env APP_URL_BASE ou localhost)
set "PAINEL_URL=http://localhost:15000"
for /f "usebackq tokens=1,* delims==" %%a in (`findstr /i /b "APP_URL_BASE=" .env 2^>nul`) do (
    set "PAINEL_URL=%%b"
)
set "PAINEL_URL=%PAINEL_URL: =%"
if "%PAINEL_URL%"=="" set "PAINEL_URL=http://localhost:15000"

REM Abre navegador apos alguns segundos (servidor sobe em paralelo)
if /i not "%ELEVA_SEM_NAVEGADOR%"=="1" (
    set "PAINEL_DASH=%PAINEL_URL%/dashboard"
    echo Abrindo navegador em %PAINEL_DASH% ...
    start "" /MIN "%~dp0abrir_navegador_atraso.bat" "%PAINEL_DASH%"
)

%PYTHON% app.py

pause
