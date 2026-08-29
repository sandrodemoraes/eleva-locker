@echo off
setlocal
chcp 65001 >nul

set "PROJETO=%~dp0.."
cd /d "%PROJETO%"
set "PROJETO=%CD%"
set "VBS=%PROJETO%\tools\iniciar_servidor.vbs"

if not exist "%VBS%" (
    echo ERRO: nao achei %VBS%
    pause
    exit /b 1
)

for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D"
set "ATALHO=%DESKTOP%\ELEVA LOCKER.lnk"

powershell -NoProfile -Command ^
  "$s = New-Object -ComObject WScript.Shell; ^
   $l = $s.CreateShortcut('%ATALHO%'); ^
   $l.TargetPath = 'wscript.exe'; ^
   $l.Arguments = '\"\"%VBS%\"\"'; ^
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
echo Atalho criado: %ATALHO%
echo Projeto: %PROJETO%
echo.
echo Se ainda fechar rapido, use duplo clique em:
echo   %PROJETO%\INICIAR ELEVA LOCKER.bat
echo.
pause
