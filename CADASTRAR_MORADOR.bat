@echo off
title ELEVA LOCKER - Cadastrar morador
cd /d "C:\ElevaLocker"
where py >nul 2>&1 && set "PY=py" || set "PY=python"

echo.
echo Exemplo Sandra (Matriz id=2):
echo   %PY% tools\cadastrar_morador.py --nome "sandra beatriz de moraes" --telefone 48996757335 --armario 2
echo.
echo Com e-mail proprio:
echo   %PY% tools\cadastrar_morador.py --nome "Nome" --telefone 48999998888 --email sandra@email.com --armario 2
echo.

set /p NOME="Nome do morador: "
set /p TEL="Telefone (DDD): "
set /p ARM="ID armario [2]: "
if "%ARM%"=="" set "ARM=2"

%PY% tools\cadastrar_morador.py --nome "%NOME%" --telefone %TEL% --armario %ARM%
pause
