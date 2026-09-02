@echo off
title ELEVA LOCKER - Instalar site piloto
color 0B
cd /d "%~dp0"

echo ============================================================
echo   INSTALAR SITE PILOTO — Modelo A (servidor local)
echo ============================================================
echo.
echo  Documentacao: docs\INSTALACAO_SITE.md
echo.
echo  Este script cria site + armario no banco e gera env.txt
echo  na pasta Sites\<codigo>\
echo.
set /p NOME=Nome do site (ex: Condominio Piloto 050): 
set /p CODIGO=Codigo (ex: piloto-050): 
set /p IP=IP fixo do PC servidor na LAN (ex: 192.168.50.10): 
set /p PORTAS=Portas do armario (8/16/24/32/64) [16]: 
if "%PORTAS%"=="" set PORTAS=16

echo.
echo  Criando site...
py tools\bootstrap_site_piloto.py ^
  --nome "%NOME%" ^
  --codigo "%CODIGO%" ^
  --ip-servidor "%IP%" ^
  --portas %PORTAS% ^
  --gerar-api-key

if errorlevel 1 (
  echo.
  echo ERRO ao criar site. Verifique Python e dependencias.
  pause
  exit /b 1
)

echo.
echo  Abrir checklist completo? (S/N)
set /p ABRIR=
if /i "%ABRIR%"=="S" start "" "docs\INSTALACAO_SITE.md"
pause
