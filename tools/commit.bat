@echo off
title ELEVA LOCKER - GIT COMMIT
color 0A
cls

echo ============================================================
echo                 ELEVA LOCKER - GIT COMMIT
echo ============================================================
echo.
echo Data: %date% %time%
echo.

:: ------------------------------------------------------------
:: Verifica se existe um repositório Git
:: ------------------------------------------------------------
git rev-parse --is-inside-work-tree >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERRO: Esta pasta nao e um repositorio Git.
    echo.
    pause
    exit /b
)

:: ------------------------------------------------------------
:: Verifica se existem alteracoes (incluindo arquivos novos)
:: ------------------------------------------------------------
git status --porcelain > "%temp%\git_status.txt"

for %%A in ("%temp%\git_status.txt") do (
    if %%~zA EQU 0 (
        del "%temp%\git_status.txt"
        echo.
        echo ============================================================
        echo Nenhuma alteracao encontrada.
        echo ============================================================
        echo.
        pause
        exit /b
    )
)

del "%temp%\git_status.txt"

:: ------------------------------------------------------------
:: Solicita a mensagem do commit
:: ------------------------------------------------------------
echo Digite a mensagem do commit:
set /p MSG=

if "%MSG%"=="" (
    echo.
    echo A mensagem do commit nao pode ficar vazia.
    echo.
    pause
    exit /b
)

echo.
echo ============================================================
echo Adicionando arquivos...
echo ============================================================
git add .

echo.
echo ============================================================
echo Criando commit...
echo ============================================================
git commit -m "%MSG%"

if %errorlevel%==0 (
    echo.
    echo ============================================================
    echo COMMIT REALIZADO COM SUCESSO!
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ERRO AO CRIAR O COMMIT!
    echo Verifique as mensagens acima.
    echo ============================================================
)

echo.
pause