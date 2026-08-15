@echo off
title ELEVA LOCKER - Iniciar servicos
color 0B

REM Atalho antigo na pasta Inicializar? Redireciona para C:\ElevaLocker (verde + armarios)
set "OFICIAL=C:\ElevaLocker"
if exist "%OFICIAL%\tools\iniciar_tudo.bat" (
    if /i not "%~dp0"=="%OFICIAL%\tools\" (
        cd /d "%OFICIAL%"
        call "%OFICIAL%\tools\iniciar_tudo.bat"
        exit /b %ERRORLEVEL%
    )
)

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

echo [1/4] Preparando bancada (SQLite + armarios)...
%PYTHON% tools\preparar_inicio_bancada.py
if errorlevel 1 (
    echo AVISO: preparar_inicio_bancada — veja acima
)

echo [2/4] Garantindo .env bancada (SQLite)...
%PYTHON% -c "import sys; sys.path.insert(0,'.'); from tools.env_bancada import garantir_bancada_env; garantir_bancada_env()"
if errorlevel 1 (
    echo AVISO: nao foi possivel ajustar .env — verifique C:\ElevaLocker\.env
)

echo [3/4] Parando servidor antigo (porta 15000)...
%PYTHON% tools\parar_servidor.py nopause 2>nul

echo [4/4] Docker WhatsApp + servidor...
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

REM Bancada: abre IP LOCAL (nao APP_URL_BASE publico — evita azul / 0 armarios)
set "PAINEL_DASH=http://192.168.16.130:15000/dashboard"
if /i not "%ELEVA_BANCADA%"=="1" (
    set "PAINEL_DASH=%PAINEL_URL%/dashboard"
    for /f "usebackq tokens=1,* delims==" %%a in (`findstr /i /b "APP_URL_BASE=" .env 2^>nul`) do (
        set "PAINEL_DASH=%%b/dashboard"
    )
    set "PAINEL_DASH=%PAINEL_DASH: =%"
)
if "%PAINEL_DASH%"=="" set "PAINEL_DASH=http://localhost:15000/dashboard"
set "PAINEL_DASH=%PAINEL_DASH:/dashboard/dashboard=/dashboard%"

REM Abre navegador apos alguns segundos (servidor sobe em paralelo)
if /i not "%ELEVA_SEM_NAVEGADOR%"=="1" (
    echo Abrindo navegador em %PAINEL_DASH% ...
    start /B "" "%~dp0abrir_navegador_atraso.bat" "%PAINEL_DASH%"
)

%PYTHON% app.py

pause
