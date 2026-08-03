@echo off
REM Localiza copias da pasta Windows (ntoskrnl) fora do sistema ativo.
REM Rode no Windows NOVO (CMD como usuario normal ou Admin).

echo ============================================================
echo  Localizar pasta Windows COPIADA (backup)
echo ============================================================
echo.
echo Sistema ativo normalmente: %SystemRoot%
echo Ignoramos essa pasta na busca principal.
echo.

set "ACHADOS=%TEMP%\elv_windows_copias.txt"
del "%ACHADOS%" >nul 2>&1

echo Procurando em discos locais (pode demorar)...
echo.

for %%D in (C D E F G H) do (
  if exist %%D:\ (
    call :probe "%%D:\Windows.old\Windows"
    call :probe "%%D:\Windows.old"
    call :probe "%%D:\Windows_antigo"
    call :probe "%%D:\Windows_backup"
    call :probe "%%D:\Backup\Windows"
    call :probe "%%D:\Backup\Windows.old"
    call :probe "%%D:\Users\%USERNAME%\Desktop\Windows"
    call :probe "%%D:\Users\%USERNAME%\Documents\Windows"
    call :probe "%%D:\Users\%USERNAME%\Windows"
    call :probe "%%D:\ElevaLocker\Windows"
    call :probe "%%D:\eleva-locker\Windows"
  )
)

REM Caminhos extras comuns apos copia manual
call :probe "%USERPROFILE%\Desktop\Windows"
call :probe "%USERPROFILE%\Documents\Windows"
call :probe "%USERPROFILE%\Windows"
call :probe "%USERPROFILE%\Desktop\Windows.old"
call :probe "%USERPROFILE%\Documents\Windows.old"

echo.
echo ========== RESULTADO ==========
if exist "%ACHADOS%" (
  type "%ACHADOS%"
  echo.
  echo Proximo passo:
  echo   06_extrair_dados_windows_antigo.bat "CAMINHO_ACHADO" "D:\Recuperado_Windows_Antigo"
) else (
  echo Nenhuma copia tipica encontrada nos caminhos padrao.
  echo.
  echo Se voce sabe a pasta, teste:
  echo   dir CAMINHO\System32\ntoskrnl.exe
  echo.
  echo Ou busque no Explorer por: ntoskrnl.exe
)
echo.
echo Doc: docs\RECUPERAR_COPIA_WINDOWS.md
echo.
pause
goto :eof

:probe
set "P=%~1"
if /I "%P%"=="%SystemRoot%" goto :eof
if exist "%P%\System32\ntoskrnl.exe" (
  echo [OK] %P%
  echo %P%>> "%ACHADOS%"
  if exist "%~dp1Users" echo      Users ao lado: %~dp1Users
  if exist "%P%\..\Users" echo      Users relativo existe
)
goto :eof
