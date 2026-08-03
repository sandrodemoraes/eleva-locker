@echo off
REM Copia tools\windows_boot para a raiz do pendrive (ex.: F:)
REM Uso: 08_copiar_scripts_para_pendrive.bat F:

setlocal
set "LETRA=%~1"
if "%LETRA%"=="" (
  echo Uso: 08_copiar_scripts_para_pendrive.bat LETRA:
  echo Exemplo: 08_copiar_scripts_para_pendrive.bat F:
  pause
  exit /b 1
)

REM Aceita F ou F:
set "LETRA=%LETRA::=%"
set "DEST=%LETRA%:\windows_boot"
set "SRC=%~dp0"

if not exist "%LETRA%:\" (
  echo ERRO: pendrive %LETRA%: nao encontrado.
  pause
  exit /b 1
)

echo Copiando scripts para %DEST% ...
mkdir "%DEST%" 2>nul
xcopy /E /I /Y "%SRC%*" "%DEST%\"
if errorlevel 1 (
  echo Falha no xcopy.
  pause
  exit /b 1
)

echo.
echo OK. No WinRE use:
echo   %LETRA%:
echo   cd \windows_boot
echo   01_listar_discos.bat
echo.
dir "%DEST%\*.bat"
pause
endlocal
