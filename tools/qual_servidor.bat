@echo off
title ELEVA LOCKER - Qual servidor?
cd /d "%~dp0.."
set "PYTHON="
where py >nul 2>&1 && set "PYTHON=py"
if not defined PYTHON where python >nul 2>&1 && set "PYTHON=python"
if not defined PYTHON where python3 >nul 2>&1 && set "PYTHON=python3"
if not defined PYTHON (echo Python nao encontrado. & pause & exit /b 1)
%PYTHON% tools\qual_servidor.py
pause
