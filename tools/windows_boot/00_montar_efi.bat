@echo off
REM Atalho: monta volume EFI escolhido em S:
REM Uso: 00_montar_efi.bat NUMERO_DO_VOLUME
REM Exemplo: 00_montar_efi.bat 2
REM Descubra o numero com: diskpart -> list vol

setlocal
set "VOL=%~1"
if "%VOL%"=="" (
    echo Uso: 00_montar_efi.bat NUMERO_DO_VOLUME
    echo Exemplo apos "list vol": 00_montar_efi.bat 2
    pause
    exit /b 1
)

echo Montando volume %VOL% como S:...
(
  echo select vol %VOL%
  echo assign letter=S
  echo exit
) > "%TEMP%\elv_mount_efi.txt"

diskpart /s "%TEMP%\elv_mount_efi.txt"
del "%TEMP%\elv_mount_efi.txt" >nul 2>&1

if exist "S:\" (
    echo OK: S: montado.
    dir S:\
) else (
    echo Falhou. Confira se o volume e FAT32 EFI e se S: esta livre.
)

pause
endlocal
