@echo off
REM Extrai dados uteis de uma COPIA da pasta Windows antiga.
REM NAO altera C:\Windows do sistema atual.
REM
REM Uso:
REM   06_extrair_dados_windows_antigo.bat "D:\backup pc fabio\Windows" "D:\Recuperado_Windows_Antigo"

setlocal EnableExtensions

set "ORIG_WIN=%~f1"
set "DEST=%~2"

if "%~1"=="" (
  echo.
  echo Uso:
  echo   06_extrair_dados_windows_antigo.bat "CAMINHO\Windows" "PASTA_DESTINO"
  echo.
  echo Exemplo:
  echo   06_extrair_dados_windows_antigo.bat "D:\backup pc fabio\Windows" "D:\Recuperado_Windows_Antigo"
  echo.
  pause
  exit /b 1
)

if "%~2"=="" (
  set "DEST=D:\Recuperado_Windows_Antigo"
) else (
  set "DEST=%~f2"
)

REM Preferir PowerShell (lida melhor com espacos no caminho)
where powershell >nul 2>&1
if %errorlevel%==0 (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp006_extrair_dados_windows_antigo.ps1" -OrigWin "%ORIG_WIN%" -Dest "%DEST%"
  set "RC=%errorlevel%"
  pause
  exit /b %RC%
)

echo PowerShell nao encontrado; usando modo CMD...
goto :cmd_mode

:cmd_mode
for %%I in ("%ORIG_WIN%") do set "ORIG_PARENT=%%~dpI"
REM remove barra final do parent: %%~dpI sempre termina com \
set "ORIG_PARENT=%ORIG_PARENT:~0,-1%"

if /I "%ORIG_WIN%"=="%SystemRoot%" (
  echo ERRO: Voce apontou para o Windows ATUAL.
  pause
  exit /b 1
)

if not exist "%ORIG_WIN%\System32\ntoskrnl.exe" (
  echo ERRO: Nao achei System32\ntoskrnl.exe em:
  echo   %ORIG_WIN%
  pause
  exit /b 1
)

echo ============================================================
echo  Extrair dados do Windows ANTIGO (copia)
echo ============================================================
echo Origem Windows: %ORIG_WIN%
echo Pasta pai:      %ORIG_PARENT%
echo Destino:        %DEST%
echo.
echo Isto NAO repara boot. So copia arquivos uteis.
echo.
pause

mkdir "%DEST%" 2>nul
set "LOG=%DEST%\RECUPERACAO_LOG.txt"
> "%LOG%" echo Recuperacao iniciada
>> "%LOG%" echo Origem=%ORIG_WIN%
>> "%LOG%" echo Destino=%DEST%

call :copy_if "Users_ao_lado" "%ORIG_PARENT%\Users" "%DEST%\Users"
call :copy_if "ElevaLocker_pai" "%ORIG_PARENT%\ElevaLocker" "%DEST%\ElevaLocker"
call :copy_if "eleva-locker_pai" "%ORIG_PARENT%\eleva-locker" "%DEST%\eleva-locker"

if exist "%ORIG_PARENT%\Users\" (
  for /D %%U in ("%ORIG_PARENT%\Users\*") do (
    call :maybe_user "%%~nxU" "%%U"
  )
)

if exist "%ORIG_WIN%\System32\config\SOFTWARE" (
  mkdir "%DEST%\config_hives" 2>nul
  echo Copiando hives de registro...
  copy /Y "%ORIG_WIN%\System32\config\SOFTWARE" "%DEST%\config_hives\SOFTWARE" >nul
  copy /Y "%ORIG_WIN%\System32\config\SYSTEM" "%DEST%\config_hives\SYSTEM" >nul
  copy /Y "%ORIG_WIN%\System32\config\SAM" "%DEST%\config_hives\SAM" >nul
)

echo Buscando elevalocker.db...
where /R "%ORIG_PARENT%" elevalocker.db > "%TEMP%\elv_db_hits.txt" 2>nul
if exist "%TEMP%\elv_db_hits.txt" (
  for /f "usebackq delims=" %%F in ("%TEMP%\elv_db_hits.txt") do (
    echo [DB] %%F
    mkdir "%DEST%\databases" 2>nul
    copy /Y "%%F" "%DEST%\databases\" >nul
  )
)

echo.
echo Concluido. Veja: %DEST%
echo Log: %LOG%
pause
endlocal
exit /b 0

:maybe_user
set "UNAME=%~1"
set "UPATH=%~2"
if /I "%UNAME%"=="Public" goto :eof
if /I "%UNAME%"=="Default" goto :eof
if /I "%UNAME%"=="Default User" goto :eof
if /I "%UNAME%"=="All Users" goto :eof
call :copy_if "Desktop_%UNAME%" "%UPATH%\Desktop" "%DEST%\Users_extract\%UNAME%\Desktop"
call :copy_if "Documents_%UNAME%" "%UPATH%\Documents" "%DEST%\Users_extract\%UNAME%\Documents"
call :copy_if "Downloads_%UNAME%" "%UPATH%\Downloads" "%DEST%\Users_extract\%UNAME%\Downloads"
call :copy_if "Arduino_%UNAME%" "%UPATH%\Documents\Arduino" "%DEST%\Users_extract\%UNAME%\Arduino"
call :copy_if "eleva-locker_%UNAME%" "%UPATH%\eleva-locker" "%DEST%\Users_extract\%UNAME%\eleva-locker"
call :copy_if "ElevaLocker_%UNAME%" "%UPATH%\ElevaLocker" "%DEST%\Users_extract\%UNAME%\ElevaLocker"
goto :eof

:copy_if
set "LABEL=%~1"
set "SRC=%~2"
set "DST=%~3"
if not exist "%SRC%\" if not exist "%SRC%" (
  echo [  ] ausente: %LABEL%
  >> "%LOG%" echo [  ] ausente: %LABEL% %SRC%
  goto :eof
)
echo [OK] %LABEL%
>> "%LOG%" echo [OK] %LABEL% %SRC%
mkdir "%DST%" 2>nul
robocopy "%SRC%" "%DST%" /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS >nul
goto :eof
