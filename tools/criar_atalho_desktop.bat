@echo off
title ELEVA LOCKER - Criar atalho Area de Trabalho
cd /d "%~dp0.."

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_desktop.ps1"
pause
