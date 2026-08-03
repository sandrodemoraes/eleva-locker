@echo off
title ELEVA LOCKER - Criar atalho
color 0A
cd /d "%~dp0.."

set "PROJETO=%cd%"
set "ALVO=%PROJETO%\iniciar_elevalocker.bat"

if not exist "%ALVO%" (
    echo.
    echo ERRO: Nao foi encontrado iniciar_elevalocker.bat
    echo Pasta esperada: %PROJETO%
    echo.
    pause
    exit /b 1
)

echo ============================================================
echo         ELEVA LOCKER - Criar atalho na area de trabalho
echo ============================================================
echo.
echo Projeto: %PROJETO%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$desktop = [Environment]::GetFolderPath('Desktop'); ^
   $alvo = '%ALVO%'; ^
   $projeto = '%PROJETO%'; ^
   $caminho = Join-Path $desktop 'ElevaLocker.lnk'; ^
   $ws = New-Object -ComObject WScript.Shell; ^
   $s = $ws.CreateShortcut($caminho); ^
   $s.TargetPath = $alvo; ^
   $s.WorkingDirectory = $projeto; ^
   $s.WindowStyle = 1; ^
   $s.Description = 'Iniciar sistema ELEVA LOCKER'; ^
   $s.Save(); ^
   Write-Host ('Atalho criado: ' + $caminho)"

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel criar o atalho.
    echo.
    pause
    exit /b 1
)

echo.
echo Clique duas vezes em "ElevaLocker" na area de trabalho para iniciar.
echo.
pause
