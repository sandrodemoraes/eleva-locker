"""Imprime URLs do totem em modo quiosque (lê APP_URL_BASE e TOTEM_ARMARIO_ID do .env)."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parent.parent
env_path = ROOT / ".env"

if env_path.exists():
    for linha in env_path.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))

base = os.getenv("APP_URL_BASE", "http://192.168.16.130:15000").rstrip("/")
armario = os.getenv("TOTEM_ARMARIO_ID", "2").strip() or "2"

print(f"{base}/totem/{armario}?kiosk=1")
print(f"{base}/totem/quiosque")
print(f"{base}/totem/quiosque/fully.json")
