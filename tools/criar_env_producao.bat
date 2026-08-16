@echo off
cd /d "%~dp0.."

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"

if not defined PYTHON (
    echo.
    echo ERRO: Python nao encontrado no PATH.
    echo Instale Python em https://www.python.org/downloads/
    echo Marque "Add python.exe to PATH" na instalacao.
    echo.
    echo Se ja instalou, tente manualmente:
    echo   python tools\criar_env_producao.py
    echo   python tools\verificar_env.py
    echo.
    pause
    exit /b 1
)

echo Usando: %PYTHON%
echo.

%PYTHON% tools\criar_env_producao.py
if errorlevel 1 (
    pause
    exit /b 1
)

%PYTHON% tools\verificar_env.py
pause
