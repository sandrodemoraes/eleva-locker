@echo off
REM Copia ElevaLocker + pastas do usuario para o HD de backup.
REM Uso: 09_backup_para_hd.bat E:
REM   E: = letra do HD formatado como BACKUP_ELEVA

setlocal EnableExtensions
set "LETRA=%~1"
if "%LETRA%"=="" (
  echo Uso: 09_backup_para_hd.bat LETRA:
  echo Exemplo: 09_backup_para_hd.bat E:
  pause
  exit /b 1
)

set "LETRA=%LETRA::=%"
set "ROOT=%LETRA%:\BACKUP_ELEVA"

if not exist "%LETRA%:\" (
  echo ERRO: disco %LETRA%: nao encontrado.
  pause
  exit /b 1
)

echo ============================================================
echo  Backup para %ROOT%
echo ============================================================
echo.
echo Confirme que %LETRA%: e o HD de BACKUP (nao o C: do Windows).
pause

mkdir "%ROOT%\eleva-locker" 2>nul
mkdir "%ROOT%\PC\Documents" 2>nul
mkdir "%ROOT%\PC\Desktop" 2>nul
mkdir "%ROOT%\PC\Downloads" 2>nul
mkdir "%ROOT%\PC\Arduino" 2>nul

echo.
echo [1/4] eleva-locker ...
if exist "%USERPROFILE%\eleva-locker\" (
  robocopy "%USERPROFILE%\eleva-locker" "%ROOT%\eleva-locker" /E /COPY:DAT /R:2 /W:2 /XD .git __pycache__ .venv venv node_modules /NFL /NDL /NP
) else if exist "C:\ElevaLocker\" (
  echo Usando C:\ElevaLocker ...
  robocopy "C:\ElevaLocker" "%ROOT%\eleva-locker" /E /COPY:DAT /R:2 /W:2 /XD .git __pycache__ .venv venv node_modules /NFL /NDL /NP
) else (
  echo [AVISO] Pasta eleva-locker nao encontrada.
)

REM OneDrive redireciona Desktop/Documents em muitos PCs Windows 11
set "DOCS=%USERPROFILE%\Documents"
set "DESK=%USERPROFILE%\Desktop"
if exist "%USERPROFILE%\OneDrive\Documents\" set "DOCS=%USERPROFILE%\OneDrive\Documents"
if exist "%USERPROFILE%\OneDrive\Desktop\" set "DESK=%USERPROFILE%\OneDrive\Desktop"

echo [2/4] Documents ...
echo   origem: %DOCS%
robocopy "%DOCS%" "%ROOT%\PC\Documents" /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NP

echo [3/4] Desktop ...
echo   origem: %DESK%
robocopy "%DESK%" "%ROOT%\PC\Desktop" /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NP

echo [4/4] Downloads ...
robocopy "%USERPROFILE%\Downloads" "%ROOT%\PC\Downloads" /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NP

if exist "%DOCS%\Arduino\" (
  echo [+] Arduino sketches ...
  robocopy "%DOCS%\Arduino" "%ROOT%\PC\Arduino" /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NP
)

echo.
echo Concluido: %ROOT%
echo Log robocopy: codigos 0-7 = ok; 8+ = falha.
echo.
dir "%ROOT%"
pause
endlocal
