@echo off
REM Alternativa para discos MBR / instalacao legada (menos comum no Win 11 UEFI).
REM Uso no WinRE: 03_reparar_boot_legado.bat

echo ============================================================
echo  Reparar boot legado (MBR / bootrec)
echo ============================================================
echo.
echo Isso NAO substitui bcdboot em sistemas UEFI puros.
echo Prefira 02_reparar_boot_uefi.bat se o Windows 11 foi instalado em UEFI.
echo.
pause

bootrec /fixmbr
bootrec /fixboot
bootrec /scanos
echo.
echo Se pedir para adicionar instalacao, responda S
bootrec /rebuildbcd

echo.
echo Pronto. Reinicie: wpeutil reboot
pause
