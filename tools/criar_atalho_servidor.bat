@echo off
REM Cria atalho na Area de Trabalho apontando para iniciar_servidor.bat
set DESKTOP=%USERPROFILE%\Desktop
set ORIGEM=C:\ElevaLocker\tools\iniciar_servidor.bat
set ATALHO=%DESKTOP%\ELEVA LOCKER.lnk

if not exist "%ORIGEM%" (
    echo ERRO: %ORIGEM% nao existe. Rode este script de dentro do projeto clonado.
    pause
    exit /b 1
)

powershell -NoProfile -Command ^
  "$s = New-Object -ComObject WScript.Shell; ^
   $l = $s.CreateShortcut('%ATALHO%'); ^
   $l.TargetPath = '%ORIGEM%'; ^
   $l.WorkingDirectory = 'C:\ElevaLocker'; ^
   $l.WindowStyle = 1; ^
   $l.Description = 'Inicia servidor ELEVA LOCKER porta 15000'; ^
   $l.Save()"

if errorlevel 1 (
    echo ERRO ao criar atalho.
    pause
    exit /b 1
)

echo Atalho criado: %ATALHO%
echo Duplo clique nele para subir o servidor.
pause
