@echo off
REM Extrai dados uteis de uma COPIA da pasta Windows antiga.
REM NAO altera C:\Windows do sistema atual.
REM
REM Uso:
REM   06_extrair_dados_windows_antigo.bat "D:\Backup\Windows" "D:\Recuperado_Windows_Antigo"
REM
REM Se so passar a origem, destino = D:\Recuperado_Windows_Antigo

setlocal EnableExtensions EnableDelayedExpansion

set "ORIG_WIN=%~1"
set "DEST=%~2"

if "%ORIG_WIN%"=="" (
  echo.
  echo Uso:
  echo   06_extrair_dados_windows_antigo.bat "CAMINHO\Windows" "PASTA_DESTINO"
  echo.
  echo Exemplo:
  echo   06_extrair_dados_windows_antigo.bat "D:\Backup\Windows" "D:\Recuperado_Windows_Antigo"
  echo.
  echo Antes: rode 05_localizar_windows_copiado.bat
  echo.
  pause
  exit /b 1
)

if "%DEST%"=="" set "DEST=D:\Recuperado_Windows_Antigo"

set "ORIG_WIN=%ORIG_WIN:"=%"
set "DEST=%DEST:"=%"

REM Remove barra final
if "%ORIG_WIN:~-1%"=="\" set "ORIG_WIN=%ORIG_WIN:~0,-1%"
if "%DEST:~-1%"=="\" set "DEST=%DEST:~0,-1%"

if /I "%ORIG_WIN%"=="%SystemRoot%" (
  echo ERRO: Voce apontou para o Windows ATUAL (%SystemRoot%).
  echo Use a pasta COPIADA (Windows.old / Backup\Windows / etc.).
  pause
  exit /b 1
)

if not exist "%ORIG_WIN%\System32\ntoskrnl.exe" (
  echo ERRO: Nao achei System32\ntoskrnl.exe em:
  echo   %ORIG_WIN%
  echo Confirme o caminho com 05_localizar_windows_copiado.bat
  pause
  exit /b 1
)

for %%I in ("%ORIG_WIN%") do set "ORIG_PARENT=%%~dpI"
set "ORIG_PARENT=%ORIG_PARENT:~0,-1%"

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
echo Recuperacao %DATE% %TIME%> "%LOG%"
echo Origem=%ORIG_WIN%>> "%LOG%"
echo Destino=%DEST%>> "%LOG%"
echo.>> "%LOG%"

call :copy_if "Users (ao lado do Windows)" "%ORIG_PARENT%\Users" "%DEST%\Users"
call :copy_if "Windows.old Users" "%ORIG_PARENT%\Windows.old\Users" "%DEST%\Windows.old_Users"
call :copy_if "ElevaLocker (pai)" "%ORIG_PARENT%\ElevaLocker" "%DEST%\ElevaLocker"
call :copy_if "eleva-locker (pai)" "%ORIG_PARENT%\eleva-locker" "%DEST%\eleva-locker"
call :copy_if "ElevaLocker em C-like" "%ORIG_PARENT%\Users\%USERNAME%\eleva-locker" "%DEST%\eleva-locker_user"
call :copy_if "Arduino Documents" "%ORIG_PARENT%\Users\%USERNAME%\Documents\Arduino" "%DEST%\Arduino_sketches"

REM Varre todos os perfis em Users (se existir)
if exist "%ORIG_PARENT%\Users" (
  for /D %%U in ("%ORIG_PARENT%\Users\*") do (
    if /I not "%%~nxU"=="Public" if /I not "%%~nxU"=="Default" if /I not "%%~nxU"=="Default User" if /I not "%%~nxU"=="All Users" (
      call :copy_if "Desktop %%~nxU" "%%U\Desktop" "%DEST%\Users_extract\%%~nxU\Desktop"
      call :copy_if "Documents %%~nxU" "%%U\Documents" "%DEST%\Users_extract\%%~nxU\Documents"
      call :copy_if "Downloads %%~nxU" "%%U\Downloads" "%DEST%\Users_extract\%%~nxU\Downloads"
      call :copy_if "Arduino %%~nxU" "%%U\Documents\Arduino" "%DEST%\Users_extract\%%~nxU\Arduino"
      call :copy_if "eleva-locker %%~nxU" "%%U\eleva-locker" "%DEST%\Users_extract\%%~nxU\eleva-locker"
      call :copy_if "ElevaLocker %%~nxU" "%%U\ElevaLocker" "%DEST%\Users_extract\%%~nxU\ElevaLocker"
      call :copy_if ".cursor %%~nxU" "%%U\.cursor" "%DEST%\Users_extract\%%~nxU\.cursor"
    )
  )
)

REM Backup dos hives (somente leitura/copia — NAO instalar no Windows novo)
if exist "%ORIG_WIN%\System32\config\SOFTWARE" (
  mkdir "%DEST%\config_hives" 2>nul
  echo Copiando hives de registro (backup)...
  copy /Y "%ORIG_WIN%\System32\config\SOFTWARE" "%DEST%\config_hives\SOFTWARE" >> "%LOG%" 2>&1
  copy /Y "%ORIG_WIN%\System32\config\SYSTEM" "%DEST%\config_hives\SYSTEM" >> "%LOG%" 2>&1
  copy /Y "%ORIG_WIN%\System32\config\SAM" "%DEST%\config_hives\SAM" >> "%LOG%" 2>&1
  echo [OK] hives -^> %DEST%\config_hives>> "%LOG%"
)

REM Procura elevalocker.db em lugares tipicos do backup
echo.>> "%LOG%"
echo Buscando elevalocker.db...>> "%LOG%"
where /R "%ORIG_PARENT%" elevalocker.db > "%TEMP%\elv_db_hits.txt" 2>nul
if exist "%TEMP%\elv_db_hits.txt" (
  for /f "usebackq delims=" %%F in ("%TEMP%\elv_db_hits.txt") do (
    echo [DB] %%F
    echo [DB] %%F>> "%LOG%"
    mkdir "%DEST%\databases" 2>nul
    copy /Y "%%F" "%DEST%\databases\" >nul
  )
)

echo.
echo ============================================================
echo  Concluido. Veja: %DEST%
echo  Log: %LOG%
echo ============================================================
echo.
echo Proximo:
echo  1. Abra %DEST%\Users_extract e confira Desktop/Documents
echo  2. Se tiver databases\elevalocker.db, use no ElevaLocker novo
echo  3. Guia app: docs\RECUPERAR_SERVIDOR.md
echo  4. NAO substitua C:\Windows pela pasta antiga
echo.
pause
endlocal
exit /b 0

:copy_if
set "LABEL=%~1"
set "SRC=%~2"
set "DST=%~3"
if exist "%SRC%" (
  echo [OK] %LABEL%
  echo [OK] %LABEL%  %SRC% -^> %DST%>> "%LOG%"
  mkdir "%DST%" 2>nul
  robocopy "%SRC%" "%DST%" /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS >nul
  if errorlevel 8 (
    echo [AVISO] robocopy falhou em parte: %LABEL%
    echo [AVISO] %LABEL%>> "%LOG%"
  )
) else (
  echo [  ] ausente: %LABEL%
  echo [  ] ausente: %LABEL%  %SRC%>> "%LOG%"
)
goto :eof
