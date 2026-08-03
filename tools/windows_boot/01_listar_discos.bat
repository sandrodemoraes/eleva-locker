@echo off
REM Rode no Prompt de Comando do WinRE (Reparar o computador).
REM Lista discos e volumes para achar Windows e EFI.

echo ============================================================
echo  ELEVA LOCKER - Mapear discos (WinRE)
echo ============================================================
echo.

echo --- DISKPART: list disk ---
echo list disk > "%TEMP%\elv_diskpart.txt"
echo list vol >> "%TEMP%\elv_diskpart.txt"
echo exit >> "%TEMP%\elv_diskpart.txt"
diskpart /s "%TEMP%\elv_diskpart.txt"
del "%TEMP%\elv_diskpart.txt" >nul 2>&1

echo.
echo --- Procurando Windows nas letras C: a H: ---
for %%L in (C D E F G H) do (
    if exist "%%L:\Windows\System32\ntoskrnl.exe" (
        echo [OK] Windows encontrado em %%L:\Windows
    ) else (
        echo [  ] Sem Windows em %%L:
    )
)

echo.
echo --- Procurando EFI (bootmgfw.efi) ---
for %%L in (C D E F G H S) do (
    if exist "%%L:\EFI\Microsoft\Boot\bootmgfw.efi" (
        echo [OK] EFI Microsoft em %%L:\EFI\Microsoft\Boot
    )
)

echo.
echo Anote a letra do Windows e o volume EFI (FAT32 pequeno).
echo Depois rode: 02_reparar_boot_uefi.bat
echo.
pause
