@echo off
REM Repara boot UEFI do Windows 11.
REM Uso no WinRE: 02_reparar_boot_uefi.bat W
REM   onde W = letra da particao que contem \Windows (sem dois-pontos)

setlocal EnableExtensions
set "WINLETTER=%~1"

if "%WINLETTER%"=="" (
    echo.
    echo Uso: 02_reparar_boot_uefi.bat LETRA
    echo Exemplo: 02_reparar_boot_uefi.bat D
    echo.
    echo Descubra a letra com 01_listar_discos.bat
    echo.
    pause
    exit /b 1
)

set "WINLETTER=%WINLETTER::=%"
set "WINDIR=%WINLETTER%:\Windows"

if not exist "%WINDIR%\System32\ntoskrnl.exe" (
    echo ERRO: Nao achei %WINDIR%\System32\ntoskrnl.exe
    echo Confirme a letra com 01_listar_discos.bat
    pause
    exit /b 1
)

echo ============================================================
echo  Reparar boot UEFI
echo  Windows: %WINDIR%
echo ============================================================
echo.
echo Vai montar a particao EFI em S: (se ainda nao tiver letra).
echo Se S: ja estiver em uso, ajuste o script ou use outra letra.
echo.
pause

echo.
echo --- Montando EFI em S: via diskpart ---
(
  echo list vol
  echo select vol 0
) > "%TEMP%\elv_efi_hint.txt"

echo.
echo Abra outro diskpart se precisar: list vol, selecione o FAT32 EFI,
echo depois: assign letter=S
echo.
echo Pressione uma tecla quando a particao EFI estiver em S:...
pause >nul

if not exist "S:\" (
    echo ERRO: S: nao existe. Monte a EFI em S: e rode de novo.
    pause
    exit /b 1
)

echo.
echo --- bcdboot ---
bcdboot "%WINDIR%" /s S: /f UEFI
if errorlevel 1 (
    echo AVISO: bcdboot retornou erro. Tentando bootrec mesmo assim...
)

echo.
echo --- bootrec ---
bootrec /fixboot
bootrec /scanos
echo.
echo Se pedir para adicionar instalacao a lista, responda S
bootrec /rebuildbcd

echo.
echo Concluido. Remova o pendrive e reinicie:
echo   wpeutil reboot
echo.
pause
endlocal
