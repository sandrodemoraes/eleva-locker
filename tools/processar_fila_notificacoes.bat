@echo off
title ELEVA LOCKER - Fila notificacoes pendentes
color 0B
cd /d "%~dp0.."

echo ============================================================
echo   FILA NOTIFICACOES — reenvio manual (ajuda + encomendas)
echo ============================================================
echo.

py tools\processar_fila_notificacoes.py
pause
