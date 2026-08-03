@echo off
title ELEVA LOCKER - Remover inicio automatico
color 0C

echo ============================================================
echo      ELEVA LOCKER - Remover inicio automatico com Windows
echo ============================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$startup = [Environment]::GetFolderPath('Startup'); ^
   $caminho = Join-Path $startup 'ElevaLocker.lnk'; ^
   if (Test-Path $caminho) { ^
     Remove-Item -Force $caminho; ^
     Write-Host ('Removido: ' + $caminho) ^
   } else { ^
     Write-Host 'Nenhum atalho de inicio automatico encontrado.' ^
   }"

echo.
echo O atalho da area de trabalho NAO foi removido.
echo.
pause
