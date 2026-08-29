@echo off
setlocal
chcp 65001 >nul

REM Detecta pasta do projeto (pai de tools\)
set "PROJETO=%~dp0.."
cd /d "%PROJETO%"
set "PROJETO=%CD%"
set "BAT=%PROJETO%\tools\iniciar_servidor.bat"
set "CMD=%SystemRoot%\System32\cmd.exe"

if not exist "%BAT%" (
    echo ERRO: nao achei %BAT%
    pause
    exit /b 1
)

REM Area de trabalho (OneDrive ou local)
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D"
set "ATALHO=%DESKTOP%\ELEVA LOCKER.lnk"

powershell -NoProfile -Command ^
  "$s = New-Object -ComObject WScript.Shell; ^
   $l = $s.CreateShortcut('%ATALHO%'); ^
   $l.TargetPath = '%CMD%'; ^
   $l.Arguments = '/k \"\"%BAT%\"\"'; ^
   $l.WorkingDirectory = '%PROJETO%'; ^
   $l.WindowStyle = 1; ^
   $l.IconLocation = '%SystemRoot%\System32\imageres.dll,109'; ^
   $l.Description = 'ELEVA LOCKER - servidor porta 15000'; ^
   $l.Save()"

if errorlevel 1 (
    echo ERRO ao criar atalho.
    pause
    exit /b 1
)

echo.
echo Atalho criado:
echo   %ATALHO%
echo.
echo Projeto: %PROJETO%
echo Teste: duplo clique no atalho "ELEVA LOCKER" na area de trabalho.
echo.
pause
