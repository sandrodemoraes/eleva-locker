@echo off
title ELEVA LOCKER - Criar atalhos
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
echo    ELEVA LOCKER - Atalho na area de trabalho + inicio Windows
echo ============================================================
echo.
echo Projeto: %PROJETO%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$alvo = '%ALVO%'; ^
   $projeto = '%PROJETO%'; ^
   $ws = New-Object -ComObject WScript.Shell; ^
   $desktop = [Environment]::GetFolderPath('Desktop'); ^
   $startup = [Environment]::GetFolderPath('Startup'); ^
   $deskPath = Join-Path $desktop 'ElevaLocker.lnk'; ^
   $startPath = Join-Path $startup 'ElevaLocker.lnk'; ^
   $d = $ws.CreateShortcut($deskPath); ^
   $d.TargetPath = $alvo; ^
   $d.WorkingDirectory = $projeto; ^
   $d.WindowStyle = 1; ^
   $d.Description = 'Iniciar sistema ELEVA LOCKER'; ^
   $d.Save(); ^
   Write-Host ('Atalho area de trabalho: ' + $deskPath); ^
   $s = $ws.CreateShortcut($startPath); ^
   $s.TargetPath = $alvo; ^
   $s.Arguments = '/startup'; ^
   $s.WorkingDirectory = $projeto; ^
   $s.WindowStyle = 7; ^
   $s.Description = 'Iniciar ELEVA LOCKER com o Windows'; ^
   $s.Save(); ^
   Write-Host ('Inicio automatico Windows: ' + $startPath)"

if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel criar os atalhos.
    echo.
    pause
    exit /b 1
)

echo.
echo Pronto:
echo  - Atalho "ElevaLocker" na area de trabalho
echo  - Inicio automatico com o Windows (janela minimizada)
echo.
echo Para remover o inicio automatico, execute:
echo   tools\remover_inicio_windows.bat
echo.
pause
