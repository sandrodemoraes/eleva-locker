@echo off
cd /d "%~dp0.."
py tools\criar_env_producao.py
py tools\verificar_env.py
pause
