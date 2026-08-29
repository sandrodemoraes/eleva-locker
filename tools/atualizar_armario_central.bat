@echo off
REM Atualiza codigo completo + recria Matriz se sumiu do banco
cd /d C:\ElevaLocker

echo.
echo === [1/3] Buscar branch no GitHub ===
git fetch origin cursor/retirada-pacote-retido-c05c
if errorlevel 1 goto :erro

echo.
echo === [2/3] Atualizar codigo (git pull) ===
git pull origin cursor/retirada-pacote-retido-c05c
if errorlevel 1 goto :erro

echo.
echo === [3/3] Recriar Matriz no banco (se faltar) ===
py tools\recriar_matriz_armario.py
if errorlevel 1 goto :erro

echo.
echo ============================================================
echo   CONFERIR em /armarios:
echo   - Subtitulo: "Cadastre armarios, placas ESP..."
echo   - Coluna Portas + botao engrenagem verde
echo   - ELEVA Locker Matriz na lista
echo.
echo   Sino (topo) abre /notificacoes
echo   Engrenagem (topo) abre /configuracoes
echo.
echo   Reinicie: py app.py
echo ============================================================
goto :fim

:erro
echo.
echo ERRO. Tente: git status
pause
exit /b 1

:fim
pause
