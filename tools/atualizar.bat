@echo off
setlocal EnableDelayedExpansion
title ELEVA LOCKER - GIT ATUALIZAR
color 0A
cls
cd /d "%~dp0.."

echo ============================================================
echo               ELEVA LOCKER - ATUALIZAR DO GIT
echo ============================================================
echo.
echo Data: %date% %time%
echo.

:: ------------------------------------------------------------
:: Verifica se o Git esta instalado
:: ------------------------------------------------------------
where git >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERRO: Git nao encontrado no PATH.
    echo Instale o Git em: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

:: ------------------------------------------------------------
:: Verifica se existe um repositorio Git
:: ------------------------------------------------------------
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERRO: Esta pasta nao e um repositorio Git.
    echo.
    echo Se ainda nao baixou o projeto, use:
    echo   git clone https://github.com/sandrodemoraes/eleva-locker.git
    echo.
    pause
    exit /b 1
)

echo Pasta: %cd%
echo.

:: ------------------------------------------------------------
:: Mostra branch atual
:: ------------------------------------------------------------
for /f "delims=" %%B in ('git branch --show-current') do set "BRANCH=%%B"
echo Branch atual: %BRANCH%
echo.

:: ------------------------------------------------------------
:: Avisa se houver alteracoes locais nao salvas
:: ------------------------------------------------------------
git status --porcelain > "%temp%\git_status_eleva.txt"
for %%A in ("%temp%\git_status_eleva.txt") do (
    if not %%~zA EQU 0 (
        echo.
        echo ATENCAO: Existem alteracoes locais nao commitadas.
        echo Faça commit com tools\commit.bat antes de atualizar,
        echo ou suas mudancas podem conflitar com o GitHub.
        echo.
        echo Alteracoes pendentes:
        type "%temp%\git_status_eleva.txt"
        echo.
        set /p CONT="Deseja tentar atualizar mesmo assim? (S/N): "
        if /I not "!CONT!"=="S" (
            del "%temp%\git_status_eleva.txt" >nul 2>&1
            echo.
            echo Atualizacao cancelada.
            echo.
            pause
            exit /b 0
        )
    )
)
del "%temp%\git_status_eleva.txt" >nul 2>&1

:: ------------------------------------------------------------
:: Baixa e aplica atualizacoes
:: ------------------------------------------------------------
echo ============================================================
echo Buscando atualizacoes no GitHub...
echo ============================================================
git fetch origin
if errorlevel 1 (
    echo.
    echo ERRO ao conectar no GitHub. Verifique internet e login do Git.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Aplicando atualizacoes na branch %BRANCH%...
echo ============================================================
git pull origin "%BRANCH%"
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERRO AO ATUALIZAR.
    echo Pode haver conflito. Avise para ajudarmos a resolver.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo PROJETO ATUALIZADO COM SUCESSO!
echo ============================================================
echo.
git log -1 --oneline
echo.
pause
