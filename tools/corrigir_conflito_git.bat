@echo off
title ELEVA LOCKER - Corrigir conflitos Git (branch retida)
color 0A
cd /d "%~dp0.."

set "BRANCH=cursor/retirada-pacote-retido-c05c"

echo ============================================================
echo   CORRIGIR CONFLITOS GIT — %BRANCH%
echo ============================================================
echo.
echo  Restaura arquivos do GitHub (remove ^<^<^<^<^<^<^<^< HEAD etc.)
echo  ATENCAO: sobrescreve alteracoes locais nesses arquivos.
echo  Seu .env NAO e alterado.
echo.
pause

set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"

echo [1/4] Abortar merge pendente (se houver)...
git merge --abort 2>nul

echo [2/4] Buscar branch no GitHub...
git fetch origin %BRANCH%
if errorlevel 1 (
    echo ERRO no fetch. Verifique internet e git.
    pause
    exit /b 1
)

echo [3/4] Restaurar arquivos da branch...
git checkout origin/%BRANCH% -- ^
  database.py ^
  config.py ^
  app.py ^
  repositories/encomenda_repository.py ^
  services/encomenda_service.py ^
  services/notificacao_service.py ^
  services/dashboard_service.py ^
  routes/encomendas.py ^
  templates/encomendas.html ^
  static/css/crud.css ^
  tools/lembretes_encomenda.py ^
  tools/lembretes_encomenda.bat

if errorlevel 1 (
    echo AVISO: alguns arquivos falharam — tentando reset completo...
    git reset --hard origin/%BRANCH%
)

echo [4/4] Marcar conflitos resolvidos...
git add database.py repositories/encomenda_repository.py services/dashboard_service.py 2>nul

echo.
echo Verificando marcadores de conflito restantes...
findstr /s /m /c:"<<<<<<<" *.py repositories\*.py services\*.py routes\*.py 2>nul
if errorlevel 1 (
    echo   OK — nenhum ^<^<^<^<^<^<^< encontrado em .py
) else (
    echo   AINDA HA CONFLITOS — rode: git reset --hard origin/%BRANCH%
)

echo.
echo ============================================================
echo   Pronto. Proximo passo:
echo     py app.py
echo ============================================================
echo.
pause
